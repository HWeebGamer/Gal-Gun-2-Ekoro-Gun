"""Create checked, distinctly named edition ZIPs from a release manifest."""
import argparse
import hashlib
import json
import re
import zipfile
from pathlib import Path

parser=argparse.ArgumentParser()
parser.add_argument('version')
args=parser.parse_args()
assert re.fullmatch(r'v[0-9]+',args.version)
root=Path(__file__).resolve().parent.parent
release=root/'releases'/args.version
manifest=json.loads((release/'manifest.json').read_text())
assert manifest['version']==args.version
checksums=[]
for edition in manifest['editions']:
    entries={'README.md':(root/'README.md').read_bytes(),
             'RELEASE_NOTES.md':(release/'NOTES.md').read_bytes(),
             'EDITION.txt':(edition['edition']+' — '+args.version+'\nInstall only this edition; do not combine with the other edition.\n').encode()}
    binary_hashes=[]
    assert {f['name'] for f in edition['files']}=={'EkoroPrototype_P.pak','EkoroPrototype_P.sig'}
    for f in edition['files']:
        data=(root/'outputs'/f['source']).read_bytes()
        digest=hashlib.sha256(data).hexdigest()
        assert digest==f['sha256'] and len(data)==f['bytes']
        entries[f['name']]=data
        binary_hashes.append(f"{digest}  {f['name']}")
    entries['SHA256SUMS.txt']=('\n'.join(binary_hashes)+'\n').encode('ascii')
    target=root/'outputs'/edition['zip']
    with zipfile.ZipFile(target,'x',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for name,data in entries.items():z.writestr(name,data)
    with zipfile.ZipFile(target) as z:
        assert z.testzip() is None and set(z.namelist())==set(entries)
        for name,data in entries.items():assert z.read(name)==data
    digest=hashlib.sha256(target.read_bytes()).hexdigest()
    checksums.append(f'{digest}  {target.name}')
    print(f'Verified {target.name}: {digest}')
(root/'outputs'/f'SHA256SUMS_{args.version}.txt').write_text('\n'.join(checksums)+'\n',encoding='ascii')
