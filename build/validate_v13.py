"""Re-extract an exact tested artifact and compare filesystem content and metadata."""
import json

from pathlib import Path
RELEASE = json.loads((Path(__file__).parent/'v1.3/release.json').read_text())
REFERENCES = {k:v['reference_sha256'] for k,v in RELEASE['editions'].items()}


def compare_reference(edition, reference, work):
    # The CLI file has a hyphen; __main__ contains its verified extraction helpers.
    import __main__ as cli
    assert cli.sha(reference) == REFERENCES[edition], 'Tested reference checksum mismatch'
    ref = work / 'tested-reference'
    ref.mkdir()
    images = cli.extract(reference, ref / 'iso')
    actual, links = cli.inventory(images / 'rootfs.squashfs', ref / 'rootfs', ref / 'metadata.txt')
    rebuilt = json.loads((work / 'final-inventory.json').read_text())
    assert actual.keys() == rebuilt.keys()
    for p, row in actual.items():
        for k in ['mode', 'uid', 'gid', 'mtime', 'target', 'sha256']:
            assert row.get(k) == rebuilt[p].get(k), (p, k)
        if row['mode'][0] != 'd':
            assert row['size'] == rebuilt[p]['size'], p
    assert links == json.loads((work / 'final-hardlinks.json').read_text())
    assert (images / 'xImage').read_bytes() == (work / 'final-xImage').read_bytes()
    assert reference.read_bytes() == (work / RELEASE['editions'][edition]['filename']).read_bytes(), 'UPT must reproduce the pinned hardware-tested bytes'
    return {'sha256': cli.sha(reference), 'rootfs_sha256': cli.sha(images / 'rootfs.squashfs'),
            'paths': len(actual), 'filesystem_content_metadata_links': 'identical',
            'kernel': 'identical', 'upt_bytes_equal': reference.read_bytes() == (work / RELEASE['editions'][edition]['filename']).read_bytes()}
