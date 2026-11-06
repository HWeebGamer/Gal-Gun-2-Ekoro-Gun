"""Assemble the four v33 downloads from the tested pak and the published v28 editions."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

root = Path(__file__).resolve().parents[1]
out = root / 'outputs'
parser = argparse.ArgumentParser()
parser.add_argument('--unrealpak', required=True)
parser.add_argument('--only-sight-cooked', type=Path, required=True)
args = parser.parse_args()
tested = out / 'EkoroMuzzlePointer_v33_VacuumFade_P.pak'
sig = tested.with_suffix('.sig')
def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def pak(*arguments):
    result = subprocess.run([args.unrealpak,*map(str,arguments)],capture_output=True,text=True)
    if result.returncode:
        raise RuntimeError(result.stdout+result.stderr)

def contents(folder):
    return {p.relative_to(folder).as_posix():p for p in folder.rglob('*') if p.is_file()}

assert digest(tested)=='96eca67980f8adfd62f4558fb2cdb8d8aed4bf8bc7155bc3931c0994fac8f509'
previous=json.loads((root/'releases/v28/manifest.json').read_text())
manifest={'version':'v33','editions':[]}
with tempfile.TemporaryDirectory(dir=out) as temp:
    temp=Path(temp)
    pak(tested,'-Extract',temp/'tested')
    newest=contents(temp/'tested')
    for edition in previous['editions']:
        name=edition['edition']
        stage=temp/name
        prior=out/edition['files'][0]['source']
        assert digest(prior)==edition['files'][0]['sha256']
        assert digest(sig)==edition['files'][1]['sha256']
        pak(prior,'-Extract',stage/'base')
        files=contents(stage/'base')
        for rel in files:
            filename=Path(rel).name
            if filename.startswith(('VRGG_Pawn.','Ekoro_Prototype_Surface.','Ekoro_BaseColor.')):
                files[rel]=newest[rel]
            elif filename.startswith('SK_DevilSweeper_Grip.'):
                if name=='Laser+Sight':files[rel]=newest[rel]
                elif name=='OnlySight':files[rel]=args.only_sight_cooked/filename
        target=out/f'EkoroMuzzlePointer_v33_{name}_P.pak'
        if name=='Laser+Sight':
            shutil.copy2(tested,target)
        else:
            response=stage/'response.txt'
            response.write_text('\n'.join(f'"{src}" "../../../GalGun2/Content/VRGG/{rel}"' for rel,src in sorted(files.items())),encoding='ascii')
            pak(target,f'-create={response}','-compress')
        pak(target,'-test')
        pak(target,'-Extract',stage/'check')
        actual=contents(stage/'check')
        assert {n:digest(p) for n,p in actual.items()}=={n:digest(p) for n,p in files.items()},name
        assert len(actual)==(25 if name.startswith('Laser') else 21)
        records=[{'name':'EkoroPrototype_P'+p.suffix,'source':p.name,'bytes':p.stat().st_size,'sha256':digest(p)} for p in (target,sig)]
        manifest['editions'].append({'edition':name,'zip':f'GalGun2_VR_Ekoro_Gun_v33_{name}.zip','files':records})
        print(name,'verified',len(actual),'files')
(root/'releases/v33/manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
