"""v28: bounded rotational tremor filter on the gun and its shared pointer."""
import struct,json
from pathlib import Path
from cooked_patch import Package
root=Path(__file__).resolve().parents[1]
p=Package(root/'work/muzzle-pointer-v26/VRGG/Player/VRGG_Pawn.uasset')
owner=p.ref('VRGG_Pawn_C')
for name in ('EkoroFilterSetup','EkoroFilterReady'):
 p.add_property(name,'IsUsingDualMotionControllers',owner)
for name in ('EkoroFilterBase','EkoroFilterRaw','EkoroFilterSmoothed'):
 p.add_property(name,'CameraMove_StartingRotation',owner)
# Struct-property clone preserves the reflected HitResult type; all native
# by-reference parameters receive actual property storage, never expressions.
hit=next(e['name'] for e in p.exports if 'SweepHitResult' in e['name'])
# index() requires a unique name, so select a unique hit-result declaration.
hit=next(e['name'] for e in p.exports if 'SweepHitResult' in e['name'] and sum(x['name']==e['name'] for x in p.exports)==1)
p.add_property('EkoroFilterHit',hit,owner)
def imp(cls,name):return p.add(name,'Function',p.ref(cls))
for cls,methods in {
 '/Script/Engine.SceneComponent':['K2_GetComponentRotation','K2_SetRelativeRotation','K2_SetWorldRotation'],
 '/Script/Engine.Actor':['AddTickPrerequisiteComponent'],
 '/Script/Engine.ActorComponent':['AddTickPrerequisiteActor'],
 '/Script/HeadMountedDisplay.MotionControllerComponent':['IsTracked'],
 '/Script/Engine.KismetMathLibrary':['RLerp','Exp','Subtract_FloatFloat','Divide_FloatFloat','EqualEqual_RotatorRotator','LessEqual_FloatFloat','Greater_FloatFloat'],
}.items():
 for name in methods:imp(cls,name)
def ref(name):return p.ref('VRGG_Pawn_C.'+name)
def prop(name):return b'\x01'+struct.pack('<i',ref(name))
def call(name,args=b'',math=False):return bytes([0x68 if math else 0x1c])+struct.pack('<i',p.ref(name))+args+b'\x16'
def m(name,*args):return call('/Script/Engine.KismetMathLibrary.'+name,b''.join(args),True)
def ctx(obj,expr,result=0):return b'\x19'+obj+struct.pack('<Ii',p.size(expr),result)+expr
def f(x):return b'\x1e'+struct.pack('<f',x)
def assign(name,value):return b'\x0f'+struct.pack('<i',ref(name))+prop(name)+value
def boolean(name,value):return b'\x14'+prop(name)+bytes([0x27 if value else 0x28])
def valid(name):return call('/Script/Engine.KismetSystemLibrary.IsValid',prop(name),True)
def gun(fn,args=b'',result=0):return ctx(prop('ControllerR'),call('/Script/Engine.SceneComponent.'+fn,args),result)
def setrot(fn,name):return gun(fn,prop(name)+b'\x28'+prop('EkoroFilterHit')+b'\x27')
dt=b'\x00'+struct.pack('<i',p.ref('VRGG_Pawn_C.ReceiveTick.DeltaSeconds'))
code=bytearray();vm=0;fix=[];labels={}
def emit(c):
 global vm
 code.extend(c);vm+=p.size(c)
def jump(label,condition=None):
 global vm
 code.append(7 if condition is not None else 6);fix.append((len(code),label));code.extend(b'\0'*4);vm+=5
 if condition is not None:emit(condition)
def label(name):labels[name]=vm
jump('done',valid('ControllerR'));jump('done',valid('MotionControllerR'))
jump('setup',prop('EkoroFilterSetup'));jump('restore')
label('setup')
rel=p.ref('/Script/Engine.SceneComponent.RelativeRotation')
emit(assign('EkoroFilterBase',ctx(prop('ControllerR'),b'\x01'+struct.pack('<i',rel),rel)))
# Raw tracking first, pawn filter second, pointer component trace third.
emit(call('/Script/Engine.Actor.AddTickPrerequisiteComponent',prop('MotionControllerR')))
jump('setup_done',valid('PointerComponent'))
emit(ctx(prop('PointerComponent'),call('/Script/Engine.ActorComponent.AddTickPrerequisiteActor',b'\x17')))
label('setup_done');emit(boolean('EkoroFilterSetup',True))
label('restore');emit(setrot('K2_SetRelativeRotation','EkoroFilterBase'))
emit(assign('EkoroFilterRaw',gun('K2_GetComponentRotation',result=ref('EkoroFilterRaw'))))
jump('reset',prop('IsUsingDualMotionControllers'))
jump('reset',prop('IsCameraControlAndReticleEnabled'))
jump('reset',m('Not_PreBool',prop('ForceHideAimReticle')))
jump('reset',m('Not_PreBool',prop('EkoroStoryCursorOverride')))
jump('reset',ctx(prop('MotionControllerR'),call('/Script/HeadMountedDisplay.MotionControllerComponent.IsTracked')))
jump('reset',m('LessEqual_FloatFloat',dt,f(.05)))
jump('reset',m('Greater_FloatFloat',dt,f(0)))
jump('seed',prop('EkoroFilterReady'))
# Large deliberate changes bypass filtering. Each normalized Euler axis must
# be within 0.7 degrees; maximum possible lag is consequently tightly bounded.
jump('seed',m('EqualEqual_RotatorRotator',prop('EkoroFilterSmoothed'),prop('EkoroFilterRaw'),f(.7)))
alpha=m('Subtract_FloatFloat',f(1),m('Exp',m('Divide_FloatFloat',dt,f(-.018))))
emit(assign('EkoroFilterSmoothed',m('RLerp',prop('EkoroFilterSmoothed'),prop('EkoroFilterRaw'),alpha,b'\x27')))
emit(setrot('K2_SetWorldRotation','EkoroFilterSmoothed'));jump('done')
label('reset');emit(boolean('EkoroFilterReady',False));jump('done')
label('seed');emit(assign('EkoroFilterSmoothed',prop('EkoroFilterRaw')));emit(boolean('EkoroFilterReady',True))
label('done')
for pos,target in fix:struct.pack_into('<I',code,pos,labels[target])
i=p.index('ReceiveTick');raw=p.body(i);loc=20+4*struct.unpack_from('<i',raw,16)[0];oldvm,size=struct.unpack_from('<ii',raw,loc)
old=bytearray(raw[loc+8:loc+8+size]);d,nodes=p.parse(old)
for start,span in d.spans.items():
 if old[start] in (6,7,76):struct.pack_into('<I',old,start+1,struct.unpack_from('<I',old,start+1)[0]+vm)
combined=bytes(code)+old
d,nodes=p.parse(combined);assert d.p+d.extra==vm+oldvm
boundaries={s[1] for s in d.spans.values()}
def verify(n):
 if n[1] in ('Jump','JumpIfNot','Push'):assert int(n[2]) in boundaries
 if n[1]=='Context':
  child=n[3][-1];_,a,b=d.spans[child[0]];assert int(n[2].split()[0].split('=')[1])==b-a
 for c in n[3]:verify(c)
for n in nodes:verify(n)
p.changes[i]=raw[:loc]+struct.pack('<ii',vm+oldvm,len(combined))+combined+raw[loc+8+size:]
p.save(root/'work/muzzle-pointer-v28/VRGG/Player/VRGG_Pawn')
(root/'outputs/Stabilizer_v28_build.json').write_text(json.dumps({'time_constant_ms':18,'bypass_axis_degrees':.7,'hitch_reset_seconds':.05,'prefix_vm':vm,'late_update':'preserved; headset verification required'},indent=2))
print('Validated v28 function, jumps, contexts and persistent property storage')
