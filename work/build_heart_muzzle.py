"""v15: isolated CPU heart burst at the barrel on accepted gameplay shots."""
import struct,json
from pathlib import Path
from cooked_patch import Package
root=Path(__file__).resolve().parent.parent
p=Package(root/'UmodelSaved/Game/VRGG/Effect/Particles/Shooting/P_EcstasyShot.uasset')
def objectref(name):return p.index(name)+1
def edit(name,path,fn):
 i=p.index(name);p.changes[i]=p.edit(p.body(i),path,fn)
def array(values):return struct.pack('<i',len(values))+b''.join(struct.pack('<i',v) for v in values)
def constant(name,field,value,vector=False):
 i=p.index(name);body=p.body(i)
 fields=list(p.tags(next(body[a:b] for n,k,e,s,a,b in p.tags(body) if n==field)))
 for n,k,e,s,a,b in fields:
  if n in ('MinValue','MaxValue'):body=p.edit(body,[field,n],lambda _:struct.pack('<f',value))
  elif n in ('MinValueVec','MaxValueVec'):body=p.edit(body,[field,n],lambda _:struct.pack('<3f',value,value,value))
 count=3 if vector else 1
 body=p.edit(body,[field,'Table','Values'],lambda _:struct.pack('<i',count)+struct.pack('<'+'f'*count,*([value]*count)))
 p.changes[i]=body
# Keep only the mesh-heart emitter; do not include its original GPU sparkle cloud.
edit('P_EcstasyShot',['Emitters'],lambda _:array([objectref('ParticleSpriteEmitter_0')]))
# CPU particles move beyond the impact effect's original fixed bounds.
i=p.index('P_EcstasyShot');body=bytearray(p.body(i))
t=next(t for t in p.tags(body) if t[0]=='bUseFixedRelativeBoundingBox');body[t[3]+24]=0;p.changes[i]=bytes(body)
mods=['ParticleModuleLifetime_0','ParticleModuleSize_0','ParticleModuleColorOverLife_0','ParticleModuleLocationPrimitiveSphere_3']
edit('ParticleLODLevel_0',['Modules'],lambda _:array([objectref(s) for s in mods]))
constant('ParticleModuleLifetime_0','Lifetime',.38)
constant('ParticleModuleSize_0','StartSize',.6,True)
constant('ParticleModuleLocationPrimitiveSphere_3','StartRadius',8)
constant('ParticleModuleLocationPrimitiveSphere_3','VelocityScale',200)
# The original emitter is local-space, but the spawned component itself is fixed
# in world space. Positive-X hemisphere sends hearts out along the muzzle ray.
i=p.index('ParticleModuleLocationPrimitiveSphere_3');body=p.body(i)
tag=p.name('Negative_X')+p.name('BoolProperty')+struct.pack('<iiBB',0,0,0,0)
p.changes[i]=tag+body
# BurstList is an array of tagged ParticleBurst structs (one burst at time zero).
i=p.index('ParticleModuleSpawn_0');body=p.body(i)
t=next(t for t in p.tags(body) if t[0]=='BurstList');a,b=t[4:6];burst=bytearray(body[a:b])
assert struct.unpack_from('<i',burst)[0]==1
# Struct-array header ends after count + name/type/size/index/struct/guid (53 bytes).
start=53
assert p.ns['fname'](burst,start) in ('Count','CountLow')
burst[start:]=p.edit(bytes(burst[start:]),['Count'],lambda _:struct.pack('<i',3))
if any(t[0]=='CountLow' for t in p.tags(bytes(burst[start:]))):
 burst[start:]=p.edit(bytes(burst[start:]),['CountLow'],lambda _:struct.pack('<i',3))
p.changes[i]=p.edit(body,['BurstList'],lambda _:bytes(burst))
# Existing pink emissive heart color and alpha fade are preserved.
old='/Game/VRGG/Effect/Particles/Shooting/P_EcstasyShot';new='/Game/VRGG/Effect/Particles/Shooting/P_EkoroHearts'
p.names[p.names.index(old)]=new;p.names[p.names.index('P_EcstasyShot')]='P_EkoroHearts'
p.save(root/'work/muzzle-pointer-v15/VRGG/Effect/Particles/Shooting/P_EkoroHearts')

# The installed pawn is unchanged since v11; all v14 size changes are in PointerComponent.
p=Package(root/'work/muzzle-pointer-v11/VRGG/Player/VRGG_Pawn.uasset')
particle=p.add('P_EkoroHearts','ParticleSystem',p.add(new,'Package'),'/Script/Engine')
def prop(s):return b'\x01'+struct.pack('<i',p.ref('VRGG_Pawn_C.'+s))
def native(s,args=b''):return b'\x1c'+struct.pack('<i',p.ref(s))+args+b'\x16'
def context(obj,code,result=0):return b'\x19'+obj+struct.pack('<Ii',p.size(code),result)+code
def getter(fn,result):return context(prop('PointerComponent'),native('/Script/Engine.SceneComponent.'+fn),p.ref(result))
target=p.index('Shot');raw=p.body(target);loc=20+4*struct.unpack_from('<i',raw,16)[0];vm,sz=struct.unpack_from('<ii',raw,loc)
old=raw[loc+8:loc+8+sz];d,nodes=p.parse(old);assert old[-3:]==b'\x04\x0b\x53'
# Reuse the first assignment as a trampoline. Existing hit/shot logic executes
# after the new guarded burst, with every original VM branch target preserved.
n=nodes[0];b,ms,me=d.spans[n[0]];assert n[1]=='LetBool' and me-ms>=5
code=bytearray(b'\x06'+struct.pack('<I',vm-1)+b'\x0b'*(me-ms-5)+old[b:-1]);pos=vm-1;fix=[]
def emit(c):
 global pos
 code.extend(c);pos+=p.size(c)
def guard(c):
 global pos
 code.append(7);fix.append(len(code));code.extend(b'\0'*4);pos+=5;emit(c)
emit(old[:b]);guard(prop('IsUsingDualMotionControllers'));guard(prop('IsCameraControlAndReticleEnabled'))
guard(b'\x68'+struct.pack('<i',p.ref('/Script/Engine.KismetMathLibrary.Not_PreBool'))+prop('ForceHideAimReticle')+b'\x16')
guard(b'\x68'+struct.pack('<i',p.ref('/Script/Engine.KismetMathLibrary.NotEqual_ByteByte'))+prop('ReticleStatus')+b'\x24\x00\x16')
guard(b'\x68'+struct.pack('<i',p.ref('/Script/Engine.KismetSystemLibrary.IsValid'))+prop('PointerComponent')+b'\x16')
location=getter('K2_GetComponentLocation','VRGG_Pawn_C.GetDualMotionControllersCursorAngle.CallFunc_K2_GetComponentLocation_ReturnValue')
rotation=getter('K2_GetComponentRotation','VRGG_Pawn_C.GetDualMotionControllersCursorAngle.CallFunc_FindLookAtRotation_ReturnValue')
spawn=native('/Script/Engine.GameplayStatics.SpawnEmitterAtLocation',b'\x17'+b'\x20'+struct.pack('<i',particle)+location+rotation+b'\x23'+struct.pack('<3f',.06,.06,.06)+b'\x27')
emit(context(b'\x20'+struct.pack('<i',p.ref('/Script/Engine.Default__GameplayStatics')),spawn))
resume=pos;emit(b'\x06'+struct.pack('<I',me));emit(b'\x53')
for offset in fix:struct.pack_into('<I',code,offset,resume)
nd,nn=p.parse(code);assert nd.p+nd.extra==pos
boundaries={s[1] for s in nd.spans.values()}
def check(n):
 if n[1] in ('Jump','JumpIfNot','Push'):assert int(n[2]) in boundaries
 if n[1]=='Context':
  _,a,b=nd.spans[n[3][-1][0]];assert int(n[2].split()[0].split('=')[1])==b-a
 for c in n[3]:check(c)
for n in nn:check(n)
p.changes[target]=raw[:loc]+struct.pack('<ii',pos,len(code))+code+raw[loc+8+sz:]
p.save(root/'work/muzzle-pointer-v15/VRGG/Player/VRGG_Pawn')
report={'shot_old_VM':vm,'shot_new_VM':pos,'burst_count':3,'lifetime_seconds':.38,'spawn_scale':.06,'direction':'muzzle local positive X hemisphere','source':'isolated clone of P_EcstasyShot mesh emitter','menu_effects':False}
(root/'outputs/HeartMuzzle_v15_build.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
