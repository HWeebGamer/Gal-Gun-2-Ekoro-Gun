"""Package mutually exclusive always-on and no-laser editions, no bridge."""
import hashlib
import json
import shutil
import zipfile
from pathlib import Path

root = Path(__file__).resolve().parent.parent
out = root/'outputs/variants-v21'
manifest = {}
for label, version in [('Laser Always On',21),('No Laser',17)]:
    folder = out/label
    folder.mkdir(parents=True, exist_ok=True)
    shutil.copy2(root/f'outputs/EkoroMuzzlePointer_v{version}_P.pak',folder/'EkoroPrototype_P.pak')
    shutil.copy2(root.parent/'outputs/EkoroMuzzlePointer_v20_P.sig',folder/'EkoroPrototype_P.sig')
    text = 'Close the game. Choose ONE edition and copy its EkoroPrototype_P.pak and .sig into GalGun2/Content/Paks/~mods, replacing the previous pair. Do not install both editions or rename them to load both. Back up the old pair first. No helper or button setup is required.\n\n'
    text += ('Laser Always On: faint pink converging beam automatically active during gameplay, hidden when gameplay aiming is disabled. Includes the under-barrel attachment. Activation transform crash fix included; awaiting headset confirmation.\n' if version==21 else 'No Laser: the previously confirmed v17 build, with no beam or under-barrel laser attachment. Keeps the Ekoro gun, working menus/crosshair and brief heart effects.\n')
    (folder/'INSTALL.txt').write_text(text)
    manifest[label] = {p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in folder.iterdir() if p.suffix in ('.pak','.sig')}
    with zipfile.ZipFile(out/(label.replace(' ','_')+'_v21.zip'),'w',zipfile.ZIP_DEFLATED) as z:
        for p in folder.iterdir(): z.write(p,p.name)
(out/'SHA256.json').write_text(json.dumps(manifest,indent=2))
print(json.dumps(manifest,indent=2))
