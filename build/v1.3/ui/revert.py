#!/usr/bin/env python3
"""Generate an overlay with selected UI bugs reverted; never overwrite a firmware.
Usage: revert.py BUILD_DIRECTORY NEW_OVERLAY_DIRECTORY --bugs 2 4
Review the resulting overlay before creating a separate test firmware.
Shared hook bytes remain until every binary UI fix has been reverted.
"""
from pathlib import Path
import argparse,json,shutil

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('build',type=Path);p.add_argument('output',type=Path);p.add_argument('--bugs',type=int,nargs='+',choices=(1,2,3,4),required=True);a=p.parse_args()
    assert not a.output.exists();bugs=set(a.bugs);record=json.loads((a.build/'BINARY-PATCHES.json').read_text());manifest=json.loads((a.build/'UI-PAYLOAD-MANIFEST.json').read_text())
    shutil.copytree(a.build/'ui-generated',a.output);player=a.output/'usr/bin/hiby_player';data=bytearray(player.read_bytes())
    for change in reversed(record['patches']):
        if change['bug'] in bugs or change['bug']=='shared' and {2,3,4}<=bugs:
            offset=change['offset'];before=bytes.fromhex(change['before']);after=bytes.fromhex(change['after'])
            assert data[offset:offset+len(after)]==after;data[offset:offset+len(after)]=before
    player.write_bytes(data)
    for item in manifest:
        if item['path']=='usr/bin/hiby_player' or item['bugs'] not in bugs:continue
        dest=a.output/item['path'];original=a.build/'ui-input'/item['path']
        if original.is_file():shutil.copyfile(original,dest)
        else:dest.unlink()
    (a.output/'REVERTED-BUGS.json').write_text(json.dumps(sorted(bugs))+'\n')
    print('Reverted UI bugs',sorted(bugs),'in new overlay',a.output)
if __name__=='__main__':main()
