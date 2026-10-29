"""v18: faint, constant pink CPU mesh beam using game-native shaders."""
import struct,argparse
from pathlib import Path
from cooked_patch import Package
args=argparse.ArgumentParser();args.add_argument('--visible',action='store_true');args=args.parse_args()
version='v23' if args.visible else 'v18'
root=Path(__file__).resolve().parent.parent
p=Package(root/'UmodelSaved/Game/VRGG/Effect/Particles/Shooting/P_EcstasyShot.uasset')
def edit(name,path,fn):
 i=p.index(name);p.changes[i]=p.edit(p.body(i),path,fn)
def array(values):return struct.pack('<i',len(values))+b''.join(struct.pack('<i',x) for x in values)
def constant(name,field,value,vector=False):
 i=p.index(name);body=p.body(i);inner=next(body[a:b] for n,k,e,s,a,b in p.tags(body) if n==field)
 for n,k,e,s,a,b in p.tags(inner):
  if n in ('MinValue','MaxValue'):body=p.edit(body,[field,n],lambda _:struct.pack('<f',value))
  if n in ('MinValueVec','MaxValueVec'):body=p.edit(body,[field,n],lambda _:struct.pack('<3f',value,value,value))
 count=3 if vector else 1
 body=p.edit(body,[field,'Table','Values'],lambda raw:struct.pack('<i',struct.unpack_from('<i',raw)[0])+struct.pack('<'+'f'*((len(raw)-4)//4),*([value]*((len(raw)-4)//4))))
 p.changes[i]=body
def boolean(name,field,value):
 i=p.index(name);body=bytearray(p.body(i));t=next(t for t in p.tags(body) if t[0]==field);body[t[3]+24]=int(value);p.changes[i]=bytes(body)
edit('P_EcstasyShot',['Emitters'],lambda _:array([p.index('ParticleSpriteEmitter_0')+1]))
edit('ParticleLODLevel_0',['Modules'],lambda _:array([p.index(s)+1 for s in ('ParticleModuleLifetime_0','ParticleModuleSize_0','ParticleModuleColorOverLife_0')]))
constant('ParticleModuleLifetime_0','Lifetime',0) # UE particles with zero inverse lifetime do not age.
constant('ParticleModuleSize_0','StartSize',1,True)
constant('ParticleModuleColorOverLife_0','AlphaOverLife',.30 if args.visible else .10)
# Constant soft pink; no bright pulse or color cycling.
edit('ParticleModuleColorOverLife_0',['ColorOverLife','Table','Values'],lambda raw:struct.pack('<i6f',6,1,.08,.35,1,.08,.35))
boolean('P_EcstasyShot','bUseFixedRelativeBoundingBox',False)
boolean('ParticleModuleTypeDataMesh_0','bCameraFacing',False)
cylinder=p.add('Cylinder','StaticMesh',p.add('/Engine/BasicShapes/Cylinder','Package'),'/Script/Engine')
edit('ParticleModuleTypeDataMesh_0',['Mesh'],lambda _:struct.pack('<i',cylinder))
# Single immortal particle, born once. Emitter component is reused across frames.
i=p.index('ParticleModuleSpawn_0');body=p.body(i)
t=next(t for t in p.tags(body) if t[0]=='BurstList');burst=body[t[4]:t[5]];assert struct.unpack_from('<i',burst)[0]==1
part=burst[53:]
for field in ('Count','CountLow'):
 if any(t[0]==field for t in p.tags(part)):part=p.edit(part,[field],lambda _:struct.pack('<i',1))
p.changes[i]=p.edit(body,['BurstList'],lambda _:burst[:53]+part)
p.names[p.names.index('/Game/VRGG/Effect/Particles/Shooting/P_EcstasyShot')]='/Game/VRGG/Effect/Particles/Shooting/P_EkoroLaser'
p.names[p.names.index('P_EcstasyShot')]='P_EkoroLaser'
p.save(root/f'work/muzzle-pointer-{version}/VRGG/Effect/Particles/Shooting/P_EkoroLaser')
print(f'Laser particle built: {version}, alpha {0.30 if args.visible else 0.10}')
