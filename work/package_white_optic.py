"""Prepare mesh-only v27 test; retain all v26 gameplay assets byte-for-byte."""
from pathlib import Path
import hashlib,json,shutil
root=Path(__file__).resolve().parents[2]
payload=root/'work/optic-v27-payload'
cooked=Path('G:/GalGun2-ModWork/project/Saved/Cooked/WindowsNoEditor/GalGun2/Content/VRGG/Player/DevilSweeper')
files=sorted(p for p in payload.rglob('*') if p.is_file())
assert len(files)==25
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
before={p.relative_to(payload).as_posix():sha(p) for p in files}
for ext in ('uasset','uexp'):
 src=cooked/f'SK_DevilSweeper_Grip.{ext}'
 assert src.exists() and src.stat().st_size>1000
 shutil.copy2(src,payload/'Player/DevilSweeper'/src.name)
after={p.relative_to(payload).as_posix():sha(p) for p in files}
changed=[n for n in before if before[n]!=after[n]]
assert set(changed)=={'Player/DevilSweeper/SK_DevilSweeper_Grip.uasset','Player/DevilSweeper/SK_DevilSweeper_Grip.uexp'},changed
(root/'work/optic-v27-response.txt').write_text('\n'.join(f'"{p}" "../../../GalGun2/Content/VRGG/{p.relative_to(payload).as_posix()}"' for p in files),encoding='ascii')
(root/'outputs/white-optic-game/build-report.json').write_text(json.dumps({'changed':changed,'files':after,'alignment':'Housing centered on barrel X, +Y forward. Existing world-space crosshair retained; no collimated reticle added. Headset verification required.'},indent=2))
print('Verified: only two mesh files changed; 23 v26 assets preserved.')
