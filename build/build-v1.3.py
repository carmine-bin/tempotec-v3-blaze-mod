#!/usr/bin/env python3
"""Reproduce an allowlisted v1.3 edition; never replace tested release images."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import stat
import subprocess
import sys
import zlib

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / 'build/v1.3'))
OFFICIAL = '5aa1bf262e9241737086076eef0f238e54e75ae226fa0c845d126de11ac01e95'
PATCHES = {
    'usr/lib/libldacdec.so.1': (0x3b80, '10004010', '10000010',
        '0427893de5def29975bc3bdf578fef32bc6e6300b73801d4813f0f918ceedb49',
        '0f6e179f2e7fd31b5700cd0f0bbfaa4fca25b56201439c0c5b64eee96e14ca2d'),
    'usr/bin/hiby_player': (0x38240, '08da100c', '00000000',
        '143c926f3b767fd7cbc63dcae0e0e3988a4b3a7e1a324afc0212eec7f90e0001',
        'ab7623fb8ea21e410068a12b484fcb848eff829eaa190774c58f7d371d2913b4'),
}
# Whole-line configuration edits; every other byte stays official.
CONFIG_EDITS = {
    'etc/bluetooth/main.conf': (
        [('ControllerMode = dual', 'ControllerMode = bredr'),
         ('FastConnectable = true', 'FastConnectable = false')],
        '0ea56014cf967b2e88165ccf2ef2c6076b64123f22c36b0f1ea0007f243308d4',
        'a29ec0f8754b9e618d4e944e9060c7461f631281b668baccf184133a7587708a'),
}
EDITION_FIXES = {'usr/lib/libldacdec.so.1', 'etc/bluetooth/main.conf'}


def edit_config(rel, data):
    edits, before_hash, after_hash = CONFIG_EDITS[rel]
    assert hashlib.sha256(data).hexdigest() == before_hash, rel
    lines = data.split(b'\n')
    for old, new in edits:
        hits = [i for i, line in enumerate(lines) if line == old.encode()]
        assert len(hits) == 1, (rel, old)
        lines[hits[0]] = new.encode()
    data = b'\n'.join(lines)
    assert hashlib.sha256(data).hexdigest() == after_hash, rel
    return data


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def save(p, value):
    p.write_text(json.dumps(value, indent=2) + '\n')


def extract(upt, dest):
    """Independent ISO trees, extraction and full OTA chain verification."""
    from iso_reader import iso_tree
    dest.mkdir()
    rr, jj = iso_tree(upt), iso_tree(upt, True)
    assert {p: r['sha256'] for p, r in rr.items() if not r['directory']} == {
        p: r['sha256'] for p, r in jj.items() if not r['directory']}
    subprocess.run(['bsdtar', '-xf', str(upt), '-C', str(dest)], check=True)
    for p, row in rr.items():
        if not row['directory']:
            assert sha(dest / p) == row['sha256'], p
    images = dest.parent / 'images'
    images.mkdir()
    ota = dest / 'ota_v0'
    names = set()
    for block in (ota / 'ota_update.in').read_text().strip().split('\n\n'):
        kv = dict(x.split('=', 1) for x in block.splitlines() if '=' in x)
        if 'img_name' not in kv:
            continue
        name, whole = kv['img_name'], kv['img_md5']
        assert name in {'xImage', 'rootfs.squashfs'} and name not in names
        names.add(name)
        chunks = sorted(ota.glob(name + '.[0-9][0-9][0-9][0-9].*'))
        hashes = (ota / f'ota_md5_{name}.{whole}').read_text().splitlines()
        assert len(chunks) == len(hashes) and chunks
        previous, payload = whole, bytearray()
        for i, (chunk, digest) in enumerate(zip(chunks, hashes)):
            assert chunk.name == f'{name}.{i:04d}.{previous}'
            data = chunk.read_bytes()
            assert len(data) == 524288 or (i == len(chunks)-1 and 0 < len(data) < 524288)
            assert hashlib.md5(data).hexdigest() == digest
            payload.extend(data)
            previous = digest
        assert len(payload) == int(kv['img_size'])
        assert hashlib.md5(payload).hexdigest() == whole
        (images / name).write_bytes(payload)
    assert names == {'xImage', 'rootfs.squashfs'}
    kernel = (images / 'xImage').read_bytes()
    header = bytearray(kernel[:64])
    assert header[:4] == bytes.fromhex('27051956')
    crc = int.from_bytes(header[4:8], 'big')
    header[4:8] = bytes(4)
    assert zlib.crc32(header) == crc
    size = int.from_bytes(kernel[12:16], 'big')
    assert zlib.crc32(kernel[64:64+size]) == int.from_bytes(kernel[24:28], 'big')
    (images / 'kernel-decompressed.bin').write_bytes(zlib.decompress(kernel[16992:], 31))
    return images


def inventory(image, tree, log):
    from build_rootfs import metadata
    records = metadata(image, log)
    subprocess.run(['unsquashfs', '-no-progress', '-d', str(tree), str(image)],
                   check=True, stdout=subprocess.DEVNULL)
    groups = {}
    for p, m in records.items():
        f = tree / p
        assert stat.filemode(f.lstat().st_mode)[0] == m['mode'][0]
        if m['mode'][0] == '-':
            m['sha256'] = sha(f)
        if m['mode'][0] in '-l':
            groups.setdefault(f.lstat().st_ino, []).append(p)
    links = sorted(sorted(g) for g in groups.values() if len(g) > 1)
    return records, links


def validate_layouts(stock, final):
    from layout import load, nodes, validate_order
    count = contracts = 0
    missing = []
    for p in sorted((stock / 'usr/resource/layout/theme1').rglob('*')):
        if not p.is_file():
            continue
        rel = p.relative_to(stock)
        before, after = load(p), load(final / rel)
        validate_order(after)
        old, new = nodes(before), nodes(after)
        for name, obj in old.items():
            assert name in new, (rel, name)
            assert (obj['kind'], obj['parent']) == (new[name]['kind'], new[name]['parent'])
            indexed = {k for k, v in obj['node'] if re.search(r'img.*_\d+$', k)}
            assert indexed <= {k for k, v in new[name]['node']}
            contracts += 1
        refs = lambda f: {v.replace('\\', '/').replace('//', '/') for v in
            re.findall(r'"([^"\r\n]+\.(?:png|jpg|jpeg|gif))"', f.read_text())}
        absent = lambda root, values: {v for v in values if not (root / 'usr/resource/litegui/theme1' / v).is_file()}
        extra = absent(final, refs(final / rel)) - absent(stock, refs(p))
        assert not extra, (rel, extra)
        count += 1
    stock_json_exceptions = []
    for p in (final / 'usr/resource').rglob('*.json'):
        try:
            json.loads(p.read_text())
        except json.JSONDecodeError:
            rel = p.relative_to(final)
            assert (stock / rel).read_bytes() == p.read_bytes(), ('New invalid JSON', rel)
            stock_json_exceptions.append(str(rel))
    pngs = 0
    for p in final.rglob('*.png'):
        data = p.read_bytes()
        assert data[:8] == b'\x89PNG\r\n\x1a\n', p
        pos = 8
        while pos < len(data):
            length = int.from_bytes(data[pos:pos+4], 'big')
            end = pos + 12 + length
            assert end <= len(data)
            assert zlib.crc32(data[pos+4:end-4]) == int.from_bytes(data[end-4:end], 'big'), p
            pos = end
        assert pos == len(data)
        pngs += 1
    for rel in ['usr/bin/hiby_player.sh', 'usr/bin/mount_ubifs.sh']:
        subprocess.run(['sh', '-n', str(final / rel)], check=True)
    return {'layouts': count, 'named_contracts': contracts, 'pngs': pngs, 'new_missing_images': missing, 'unchanged_stock_json_exceptions': stock_json_exceptions}


def generate_ui(stock, work):
    """Regenerate the six physically validated payload files from pinned inputs."""
    from ui import patch, validate
    root, overlay = work / 'ui-input', work / 'ui-generated'
    player = bytearray((stock / 'usr/bin/hiby_player').read_bytes())
    offset, before, after, original_hash, baseline_hash = PATCHES['usr/bin/hiby_player']
    assert hashlib.sha256(player).hexdigest() == original_hash
    assert player[offset:offset+4] == bytes.fromhex(before)
    player[offset:offset+4] = bytes.fromhex(after)
    assert hashlib.sha256(player).hexdigest() == baseline_hash
    inputs = {'usr/bin/hiby_player': bytes(player)}
    prefix = 'usr/resource/layout/theme1/'
    inputs[prefix+'dialog/shutdown_timer.dlg'] = (stock / (prefix+'dialog/shutdown_timer.dlg')).read_bytes()
    inputs[prefix+'dialog/playmenu_song_info.dlg'] = (REPO / 'build/v1.3/ui/inputs/playmenu_song_info.dlg').read_bytes()
    for name in ['hiby_sub_back.view', 'hiby_set_sub_back.view', 'hiby_eq_title.view']:
        inputs[prefix+name] = (REPO / 'theme/v1.3' / (prefix+name)).read_bytes()
    for rel, data in inputs.items():
        dest = root / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)
    paths, record = patch.generate(root, overlay)
    assert record['after_sha256'] == '1f995adf13d83a44fd4b8180dafc8289d4e3ea2578979f8c5468bd7126aeaa71'
    for rel in paths:
        if rel != 'usr/bin/hiby_player':
            assert (overlay / rel).read_bytes() == (REPO / 'theme/v1.3' / rel).read_bytes(), rel
    save(work / 'BINARY-PATCHES.json', record)
    save(work / 'UI-PAYLOAD-MANIFEST.json', [{'path': p, 'bugs': b,
         'sha256': sha(overlay/p)} for p,b in paths.items()])
    validate.validate(root, overlay, work)
    return overlay

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('edition', choices=['stock-fix', 'full-mod'])
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--reference', type=Path, help='Exact hardware-tested edition UPT')
    args = parser.parse_args()
    if sys.flags.optimize:
        raise SystemExit('Do not use Python -O: validation uses assertions')
    src, work = args.input.resolve(), args.output.resolve()
    os.environ['V3_BUILD_EDITION'] = args.edition
    assert sha(src) == OFFICIAL, 'Official v1.3 checksum mismatch'
    assert not work.exists(), 'Output must not exist; no overwrite or deletion'
    for tool in ['bsdtar', 'unsquashfs', 'mksquashfs', 'xorriso', 'readelf']:
        assert shutil.which(tool), f'Missing {tool}'
    base = work / 'base'
    os.environ.update(V3_BUILD_BASE=str(base), V3_BUILD_WORK=str(work), V3_BUILD_INPUT=str(src))
    import build_rootfs
    work.mkdir(parents=True)
    (base / 'v13').mkdir(parents=True)
    extract(src, base / 'v13/iso')
    old, links = inventory(base / 'v13/images/rootfs.squashfs', base / 'v13/rootfs', work / 'official-metadata.txt')
    save(base / 'v13/inventory.json', old)
    save(base / 'v13/hardlinks.json', links)
    manifest = json.loads((REPO / f'build/v1.3/{args.edition}-manifest.json').read_text())
    ui_overlay = generate_ui(base / 'v13/rootfs', work) if args.edition == 'full-mod' else None
    reasons = {}
    binary_deltas = {}
    for row in manifest:
        rel = row['path'].lstrip('/')
        assert '..' not in Path(rel).parts and not Path(rel).is_absolute()
        assert row['before'] == old.get(rel), ('Unexpected original inventory', rel)
        if row['after']['mode'][0] != '-':
            continue
        if rel in PATCHES:
            offset, original, changed, before_hash, after_hash = PATCHES[rel]
            data = bytearray((base / 'v13/rootfs' / rel).read_bytes())
            assert hashlib.sha256(data).hexdigest() == before_hash
            assert data[offset:offset+4] == bytes.fromhex(original)
            data[offset:offset+4] = bytes.fromhex(changed)
            assert hashlib.sha256(data).hexdigest() == after_hash
            assert data[offset+4:offset+8] == (base / 'v13/rootfs' / rel).read_bytes()[offset+4:offset+8]
            if rel == 'usr/bin/hiby_player':
                data = (ui_overlay / rel).read_bytes()
            original_data = (base / 'v13/rootfs' / rel).read_bytes()
            assert len(data) == len(original_data)
            binary_deltas[rel] = [i for i,(a,b) in enumerate(zip(original_data,data)) if a != b]
        elif rel in CONFIG_EDITS:
            data = edit_config(rel, (base / 'v13/rootfs' / rel).read_bytes())
            assert data == (REPO / 'theme/v1.3' / rel).read_bytes(), rel
        else:
            data = (REPO / 'theme/v1.3' / rel).read_bytes()
        assert hashlib.sha256(data).hexdigest() == row['after']['sha256'], rel
        dest = work / 'changes' / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)
        reasons[rel] = row['reason']
    assert EDITION_FIXES <= reasons.keys()
    assert args.edition != 'stock-fix' or set(reasons) == EDITION_FIXES
    save(work / 'change-reasons.json', reasons)
    save(work / 'binary-deltas.json', binary_deltas)
    # Validate before packing using a staging content tree; metadata is supplied explicitly by TAR.
    stage = work / 'stage'
    shutil.copytree(base / 'v13/rootfs', stage, symlinks=True)
    for rel in reasons:
        dest = stage / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(work / 'changes' / rel, dest)
    checks = validate_layouts(base / 'v13/rootfs', stage)
    for rel in {'usr/lib/libldacdec.so.1'} & reasons.keys():
        assert subprocess.check_output(['readelf', '-aW', str(stage / rel)]) == subprocess.check_output(['readelf', '-aW', str(base / 'v13/rootfs' / rel)])
    save(work / 'staging-validation.json', {'status': 'PASS', **checks})
    build_rootfs.build()
    import package
    package.package()
    release = json.loads((REPO/'build/v1.3/release.json').read_text())
    assert sha(work/package.NAME) == release['editions'][args.edition]['reference_sha256'], 'Package differs from the pinned validated edition'
    final = json.loads((work / 'final-inventory.json').read_text())
    assert set(final) == set(old) | {x['path'].lstrip('/') for x in manifest}
    for row in manifest:
        actual = final[row['path'].lstrip('/')]
        for k in ['mode', 'uid', 'gid', 'mtime', 'target', 'sha256']:
            assert actual.get(k) == row['after'].get(k), (row['path'], k)
    report = {'status': 'PASS', 'version': json.loads((REPO/'build/v1.3/release.json').read_text())['version'], 'edition': args.edition, 'official_sha256': sha(src),
              'reproduced_sha256': sha(work / package.NAME), 'layouts': checks,
              'release_artifact_replaced': False}
    if args.reference:
        from validate_v13 import compare_reference
        report['reference'] = compare_reference(args.edition, args.reference.resolve(), work)
    save(work / 'REPRODUCTION-REPORT.json', report)
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
