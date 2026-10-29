"""v18: persistent, default-off converging laser; right Quest A toggles it."""
import struct,json,argparse
from pathlib import Path
from cooked_patch import Package
args=argparse.ArgumentParser();args.add_argument('--bridge',action='store_true');args.add_argument('--always-on',action='store_true');args=args.parse_args()
version='v21' if args.always_on else ('v20' if args.bridge else 'v18')
toggle_key='F8' if args.bridge else 'MotionController_Right_FaceButton1'
root=Path(__file__).resolve().parent.parent
p=Package(root/'work/muzzle-pointer-v14/VRGG/Actors/PointerComponent.uasset')
engine=p.add('/Script/Engine','Package')
psc=p.add('ParticleSystemComponent','Class',engine)
owner=p.ref('PointerComponent_C')
beam=p.add_property('EkoroLaserBeam','DynamicMaterial',owner,psc)
enabled=p.add_property('EkoroLaserEnabled','CallFunc_IsValid_ReturnValue',owner)
def imp(owner,fn):return p.add(fn,'Function',p.ref(owner))
for cls,functions in {
 '/Script/Engine.GameplayStatics':['SpawnEmitterAtLocation','GetPlayerController'],
 '/Script/Engine.SceneComponent':['GetUpVector','SetVisibility'],
 '/Script/Engine.KismetMathLibrary':['MakeRotFromZ','Divide_FloatFloat','BooleanAND','MakeVector'],
}.items():
 for fn in functions:imp(cls,fn)
pc=p.add('PlayerController','Class',engine);p.add('WasInputKeyJustPressed','Function',pc)
keytype=p.add('Key','ScriptStruct',p.add('/Script/InputCore','Package'))
laser=p.add('P_EkoroLaser','ParticleSystem',p.add('/Game/VRGG/Effect/Particles/Shooting/P_EkoroLaser','Package'),'/Script/Engine')
def prop(s):return b'\x01'+struct.pack('<i',p.ref('PointerComponent_C.'+s))
def local(s):return b'\x00'+struct.pack('<i',p.ref('PointerComponent_C.ExecuteUbergraph_PointerComponent.'+s))
def native(s,args=b'',math=False):return bytes([0x68 if math else 0x1c])+struct.pack('<i',p.ref(s))+args+b'\x16'
def math(s,*args):return native('/Script/Engine.KismetMathLibrary.'+s,b''.join(args),True)
def fl(v):return b'\x1e'+struct.pack('<f',v)
def vector(x,y,z):return b'\x23'+struct.pack('<3f',x,y,z)
def context(obj,expr,result=0):return b'\x19'+obj+struct.pack('<Ii',p.size(expr),result)+expr
def valid(obj):return native('/Script/Engine.KismetSystemLibrary.IsValid',obj,True)
def get(fn):return native('/Script/Engine.SceneComponent.'+fn)
def external(fn,args=b'',result=0):return context(b'\x20'+struct.pack('<i',p.ref('/Script/Engine.Default__GameplayStatics')),native('/Script/Engine.GameplayStatics.'+fn,args),result)
ownerexpr=b'\x2e'+struct.pack('<i',p.ref('/Game/VRGG/Player/VRGG_Pawn.VRGG_Pawn_C'))+native('/Script/Engine.ActorComponent.GetOwner')
def flag(name):
 r=p.ref('/Game/VRGG/Player/VRGG_Pawn.VRGG_Pawn_C.'+name)
 return context(ownerexpr,b'\x01'+struct.pack('<i',r),r)
source=math('Add_VectorVector',get('K2_GetComponentLocation'),math('Add_VectorVector',math('Multiply_VectorFloat',get('GetUpVector'),fl(-2.248535)),math('Multiply_VectorFloat',get('GetForwardVector'),fl(.15))))
delta=math('Subtract_VectorVector',prop('HitLocation'),source)
mid=math('Multiply_VectorFloat',math('Add_VectorVector',source,prop('HitLocation')),fl(.5))
rotation=math('MakeRotFromZ',delta)
scale=math('MakeVector',fl(.001),fl(.001),math('Divide_FloatFloat',math('VSize',delta),fl(100)))
transform=math('MakeTransform',mid,rotation,scale)
target=p.index('ExecuteUbergraph_PointerComponent');raw=p.body(target);loc=20+4*struct.unpack_from('<i',raw,16)[0];oldvm,sz=struct.unpack_from('<ii',raw,loc)
old=raw[loc+8:loc+8+sz];d,nodes=p.parse(old)
# This test immediately follows the original AimReticle SetWorldTransform.
n=next(n for n in nodes if n[1]=='LetBool' and n[3][0][2].endswith('.CallFunc_IsValid_ReturnValue2'))
a=n[0];b,ms,me=d.spans[a]
program=bytearray(old[:a]+b'\x06'+struct.pack('<I',oldvm-1)+b'\x0b'*(me-ms-5)+old[b:-1]);vm=oldvm-1;fix=[];labels={}
def emit(c):
 global vm
 program.extend(c);vm+=p.size(c)
def jump(label,condition=None):
 global vm
 program.append(7 if condition is not None else 6);fix.append((len(program),label));program.extend(b'\0'*4);vm+=5
 if condition is not None:emit(condition)
def label(s):labels[s]=vm
def visible(value):return context(prop('EkoroLaserBeam'),native('/Script/Engine.SceneComponent.SetVisibility',bytes([0x27 if value else 0x28])+b'\x28'))
emit(old[a:b])
jump('hide',valid(ownerexpr));jump('hide',flag('IsUsingDualMotionControllers'))
jump('hide',flag('IsCameraControlAndReticleEnabled'));jump('hide',math('Not_PreBool',flag('ForceHideAimReticle')))
if not args.always_on:
 controller=external('GetPlayerController',b'\x17\x25',p.ref('PointerComponent_C.ExecuteUbergraph_PointerComponent.CallFunc_GetOwner_ReturnValue'))
 key=b'\x2f'+struct.pack('<ii',keytype,32)+b'\x21'+p.name(toggle_key)+b'\x30'
 pressed=context(controller,native('/Script/Engine.PlayerController.WasInputKeyJustPressed',key),p.ref('PointerComponent_C.ExecuteUbergraph_PointerComponent.CallFunc_IsValid_ReturnValue'))
 jump('after_toggle',pressed)
 emit(b'\x14'+prop('EkoroLaserEnabled')+math('Not_PreBool',prop('EkoroLaserEnabled')))
 label('after_toggle');jump('hide',prop('EkoroLaserEnabled'))
jump('spawn',valid(prop('EkoroLaserBeam')));jump('update')
label('spawn')
spawn=external('SpawnEmitterAtLocation',b'\x17'+b'\x20'+struct.pack('<i',laser)+source+b'\x22'+struct.pack('<3f',0,0,0)+vector(0,0,0)+b'\x28',beam)
emit(b'\x5f'+prop('EkoroLaserBeam')+spawn)
label('update');jump('return',valid(prop('EkoroLaserBeam')))
if args.always_on:
 transform_local=local('CallFunc_MakeTransform_ReturnValue')
 emit(b'\x0f'+struct.pack('<i',p.ref('PointerComponent_C.ExecuteUbergraph_PointerComponent.CallFunc_MakeTransform_ReturnValue'))+transform_local+transform)
 transform=transform_local
emit(context(prop('EkoroLaserBeam'),native('/Script/Engine.SceneComponent.K2_SetWorldTransform',transform+b'\x28'+local('CallFunc_K2_SetWorldTransform_SweepHitResult')+b'\x27')))
emit(visible(True));jump('return')
label('hide');jump('return',valid(prop('EkoroLaserBeam')));emit(visible(False))
label('return');emit(b'\x06'+struct.pack('<I',me));emit(b'\x53')
for offset,s in fix:struct.pack_into('<I',program,offset,labels[s])
nd,nn=p.parse(program);assert nd.p+nd.extra==vm
boundaries={s[1] for s in nd.spans.values()}
def check(n):
 if n[1] in ('Jump','JumpIfNot','Push'):assert int(n[2]) in boundaries
 if n[1]=='Context':
  _,lo,hi=nd.spans[n[3][-1][0]];assert int(n[2].split()[0].split('=')[1])==hi-lo
 for c in n[3]:check(c)
for n in nn:check(n)
p.changes[target]=raw[:loc]+struct.pack('<ii',vm,len(program))+program+raw[loc+8+sz:]
p.save(root/f'work/muzzle-pointer-{version}/VRGG/Actors/PointerComponent')
report={'old_VM':oldvm,'new_VM':vm,'tail_VM':oldvm-1,'resume_VM':me,'key':None if args.always_on else toggle_key,'quest_button':None if args.always_on else 'Right A','default_enabled':args.always_on,'always_on':args.always_on,'beam_diameter_cm':.1,'beam_alpha':.10,'source_offset_cm':[.15,0,-2.248535],'new_fields':[beam,enabled]}
(root/f'outputs/Laser_{version}_build.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
