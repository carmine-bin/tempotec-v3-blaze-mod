"""Re-extract an exact tested artifact and compare filesystem content and metadata."""
import json

REFERENCES = {
    'stock-fix': '273f56607d477d44bd071c1a3e2097361610c2e403cfddc7ccf51b98a56210d1',
    'full-mod': 'fbb6f356cea7cae73b7af39ade9d32e0e4b0f9fc1eaab4a6ac401f6e92a4c933',
}


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
    return {'sha256': cli.sha(reference), 'rootfs_sha256': cli.sha(images / 'rootfs.squashfs'),
            'paths': len(actual), 'filesystem_content_metadata_links': 'identical',
            'kernel': 'identical', 'upt_bytes_equal': reference.read_bytes() == (work / 'reproduced.upt').read_bytes()}
