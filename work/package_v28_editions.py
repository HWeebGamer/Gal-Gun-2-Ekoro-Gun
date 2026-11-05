"""Build and verify four mutually exclusive v28 attachment editions."""
import argparse,hashlib,json,shutil,subprocess
from pathlib import Path
args=argparse.ArgumentParser()
args.add_argument('--unrealpak',required=True)
args.add_argument('--only-sight-cooked',type=Path,required=True)
args=args.parse_args()
root=Path(__file__).resolve().parents[1]
release=root/'releases/v28';release.mkdir(parents=True,exist_ok=True)
stage=root/'outputs/editions-v28';stage.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def run(*cmd):
 result=subprocess.run([str(x) for x in cmd],capture_output=True,text=True)
 if result.returncode:raise RuntimeError(result.stdout+result.stderr)
 return result.stdout
manifest={'version':'v28','editions':[]}
shared_pawn=root/'work/muzzle-pointer-v28/VRGG/Player'
for edition,laser,sight in [('Laser+Sight',True,True),('NoAttachments',False,False),('LaserNoSight',True,False),('OnlySight',False,True)]:
 base=root/('work/release-v28-base-laser' if laser else 'work/release-v28-base-nolaser')
 payload=stage/edition/'payload'
 shutil.copytree(base,payload,dirs_exist_ok=True)
 for ext in ('uasset','uexp'):
  shutil.copy2(shared_pawn/f'VRGG_Pawn.{ext}',payload/'Player'/f'VRGG_Pawn.{ext}')
  if sight:
   mesh=(root.parent/'work/optic-v27-payload/Player/DevilSweeper' if laser else args.only_sight_cooked)
   shutil.copy2(mesh/f'SK_DevilSweeper_Grip.{ext}',payload/'Player/DevilSweeper'/f'SK_DevilSweeper_Grip.{ext}')
 files=sorted(p for p in payload.rglob('*') if p.is_file())
 assert len(files)==(25 if laser else 21)
 allowed={'Player/VRGG_Pawn.uasset','Player/VRGG_Pawn.uexp'}
 if sight:allowed|={'Player/DevilSweeper/SK_DevilSweeper_Grip.uasset','Player/DevilSweeper/SK_DevilSweeper_Grip.uexp'}
 changed={p.relative_to(payload).as_posix() for p in files if sha(p)!=sha(base/p.relative_to(payload))}
 assert changed==allowed,(edition,changed)
 response=stage/edition/'response.txt'
 response.write_text('\n'.join(f'"{p}" "../../../GalGun2/Content/VRGG/{p.relative_to(payload).as_posix()}"' for p in files),encoding='ascii')
 pak=root/'outputs'/f'EkoroMuzzlePointer_v28_{edition}_P.pak'
 if edition=='Laser+Sight':shutil.copy2(root/'outputs/EkoroMuzzlePointer_v28_StabilizerTest_P.pak',pak)
 else:run(args.unrealpak,pak,f'-create={response}','-compress')
 log=run(args.unrealpak,pak,'-test')
 (stage/edition/'archive-test.txt').write_text(log)
 check=stage/edition/'extracted';run(args.unrealpak,pak,'-Extract',check)
 expected={p.relative_to(payload).as_posix():sha(p) for p in files}
 actual={p.relative_to(check).as_posix():sha(p) for p in check.rglob('*') if p.is_file()}
 assert actual==expected,edition
 records=[]
 for name,src in [('EkoroPrototype_P.pak',pak),('EkoroPrototype_P.sig',root/'outputs/EkoroMuzzlePointer_v28_StabilizerTest_P.sig')]:
  records.append({'name':name,'source':src.name,'bytes':src.stat().st_size,'sha256':sha(src)})
 manifest['editions'].append({'edition':edition,'zip':f'GalGun2_VR_Ekoro_Gun_v28_{edition}.zip','files':records})
 print(f'{edition}: {len(files)} files validated; common v28 pawn confirmed')
(release/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
