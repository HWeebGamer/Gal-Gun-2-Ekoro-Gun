"""Package the exact user-tested v12 binaries; verify archive bytes."""
from pathlib import Path
import hashlib
import json
import zipfile

root = Path(__file__).resolve().parent.parent
out = root / 'outputs'
manifest = json.loads((root / 'releases/v12/manifest.json').read_text())
readme = """Gal*Gun 2 VR - Ekoro Gun Mod (v12)
Packaged October 28, 2026

FEATURES
Ekoro gun model on the right-hand weapon, barrel-aligned gameplay crosshair,
and gun-pointer menu navigation with trigger selection.
User confirmed this version works on their Meta Quest 2 PC VR setup.
Tested against the Windows Steam game, build 3345483. Other builds/headsets
have not been verified. Requires a working Gal*Gun 2 VR installation.
Two-handed grip is not included.

INSTALL
1. Close Gal*Gun 2.
2. In Steam, open the game's Properties > Installed Files > Browse.
3. Open GalGun2\\Content\\Paks and create a folder named ~mods if needed.
4. Extract EkoroPrototype_P.pak AND EkoroPrototype_P.sig from this ZIP
   directly into ~mods. README.txt and SHA256SUMS.txt are optional there.
   Do not place the ZIP itself in ~mods or add another nested folder.
5. Launch the game in VR normally.

Final layout beneath the game installation:
  GalGun2\\Content\\Paks\\~mods\\EkoroPrototype_P.pak
  GalGun2\\Content\\Paks\\~mods\\EkoroPrototype_P.sig

No Unreal Engine, Blender, UModel, or extraction key is needed to install.
Keep the matching .pak and .sig together with these exact filenames.
Before replacing an older copy, back up its .pak and .sig outside Paks.
Remove older versions of this mod from Paks, even if named differently.
Other mods that replace the same weapon, pawn, or menu assets may conflict.
Do not replace or delete the original game .pak/.sig archives.

USE
Aim the right-hand gun at menu buttons and use the trigger to select.
This release preserves the tested menu diagnostic crosshair colors:
green = interactable widget; cyan = hit-testable widget; orange = widget
component without a hit-testable path; red = no widget component hit;
magenta = invalid interaction component. These colors are intentional.

UNINSTALL
Close the game and remove only EkoroPrototype_P.pak and EkoroPrototype_P.sig
from ~mods. Restore your previous mod pair if you made a backup.

PACKAGE
This is the exact working v12 build, with no additional gameplay changes.
SHA256SUMS.txt contains checksums for both mod files.
Unofficial fan mod; not affiliated with the game's developers or publisher.
"""
entries = {'README.txt': readme.replace('\n', '\r\n').encode('utf-8')}
checksums = []
for entry in manifest:
    assert entry['Version'] == 'muzzle-pointer-v12-menu-ray-alignment'
    name = entry['Name']
    assert name in ('EkoroPrototype_P.pak', 'EkoroPrototype_P.sig')
    source = out / ('EkoroMuzzlePointer_v12_P' + Path(name).suffix)
    data = source.read_bytes()
    digest = hashlib.sha256(data).hexdigest()
    assert digest.upper() == entry['SHA256'] and len(data) == entry['Bytes']
    entries[name] = data
    checksums.append(f'{digest}  {name}')
assert len(checksums) == 2
entries['SHA256SUMS.txt'] = ('\r\n'.join(checksums) + '\r\n').encode('ascii')
dest = out / 'GalGun2_VR_Ekoro_Gun_v12.zip'
assert not dest.exists(), 'Do not overwrite a previously shared release'
with zipfile.ZipFile(dest, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
    for name, data in entries.items():
        archive.writestr(name, data)
with zipfile.ZipFile(dest) as archive:
    assert archive.testzip() is None
    assert set(archive.namelist()) == set(entries)
    for name, data in entries.items():
        assert archive.read(name) == data
print(json.dumps({'zip': str(dest), 'bytes': dest.stat().st_size,
                  'entries': list(entries), 'verified': True}, indent=2))
