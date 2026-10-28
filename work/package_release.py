"""Package verified release binaries and instructions without modifying them."""
import argparse
import hashlib
import json
import re
import zipfile
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument('version', help='Release identifier, for example v14')
args = parser.parse_args()
assert re.fullmatch(r'v[0-9]+', args.version), 'Expected a version such as v14'
root = Path(__file__).resolve().parent.parent
release = root / 'releases' / args.version
manifest = json.loads((release / 'manifest.json').read_text(encoding='utf-8-sig'))
assert {e['Name'] for e in manifest} == {'EkoroPrototype_P.pak', 'EkoroPrototype_P.sig'}
assert len(manifest) == 2
entries = {'README.md': (root / 'README.md').read_bytes(),
           'RELEASE_NOTES.md': (release / 'NOTES.md').read_bytes()}
checksums = []
for entry in manifest:
    source = root / 'outputs' / ('EkoroMuzzlePointer_' + args.version + '_P' + Path(entry['Name']).suffix)
    data = source.read_bytes()
    digest = hashlib.sha256(data).hexdigest()
    assert digest.upper() == entry['SHA256'].upper() and len(data) == entry['Bytes'], source
    entries[entry['Name']] = data
    checksums.append(f"{digest}  {entry['Name']}")
entries['SHA256SUMS.txt'] = ('\n'.join(checksums) + '\n').encode('ascii')
dest = root / 'outputs' / f'GalGun2_VR_Ekoro_Gun_{args.version}.zip'
with zipfile.ZipFile(dest, 'x', zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
    for name, data in entries.items():
        archive.writestr(name, data)
with zipfile.ZipFile(dest) as archive:
    assert archive.testzip() is None
    assert set(archive.namelist()) == set(entries)
    for name, data in entries.items():
        assert archive.read(name) == data
print(json.dumps({'zip': str(dest), 'sha256': hashlib.sha256(dest.read_bytes()).hexdigest(),
                  'bytes': dest.stat().st_size, 'verified': True}, indent=2))
