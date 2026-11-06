"""v29: subtle emblem pulse, driven by the existing accepted-shot effect path."""
import struct,json
from pathlib import Path
from cooked_patch import Package
root=Path(__file__).resolve().parents[1]
p=Package(root/'work/muzzle-pointer-v28/VRGG/Player/VRGG_Pawn.uasset')
owner=p.ref('VRGG_Pawn_C')
p.add_property('EkoroHeartMID','ControllerR',owner,p.ref('/Script/Engine.MaterialInstanceDynamic'))
p.add_property('EkoroHeartPulse','DeltaTime',owner)
for cls,fn in [('/Script/Engine.PrimitiveComponent','CreateDynamicMaterialInstance'),('/Script/Engine.MaterialInstanceDynamic','SetScalarParameterValue')]:p.add(fn,'Function',p.ref(cls))
def ref(n):return p.ref('VRGG_Pawn_C.'+n)
def prop(n):return b'\x01'+struct.pack('<i',ref(n))
def call(n,args=b'',math=False):return bytes([0x68 if math else 0x1c])+struct.pack('<i',p.ref(n))+args+b'\x16'
def math(n,*args):return call('/Script/Engine.KismetMathLibrary.'+n,b''.join(args),True)
def ctx(obj,c,result=0):return b'\x19'+obj+struct.pack('<Ii',p.size(c),result)+c
def valid(n):return call('/Script/Engine.KismetSystemLibrary.IsValid',prop(n),True)
def fl(v):return b'\x1e'+struct.pack('<f',v)
def assign(value):return b'\x0f'+struct.pack('<i',ref('EkoroHeartPulse'))+prop('EkoroHeartPulse')+value
def update():return ctx(prop('EkoroHeartMID'),call('/Script/Engine.MaterialInstanceDynamic.SetScalarParameterValue',b'\x21'+p.name('EkoroHeartPulse')+prop('EkoroHeartPulse')))
def script(name):
 i=p.index(name);raw=p.body(i);loc=20+4*struct.unpack_from('<i',raw,16)[0];vm,size=struct.unpack_from('<ii',raw,loc)
 return i,raw,loc,vm,raw[loc+8:loc+8+size],raw[loc+8+size:]
def save(info,code):
 i,raw,loc,_,_,tail=info;d,nodes=p.parse(code);boundaries={s[1] for s in d.spans.values()}
 def check(n):
  if n[1] in ('Jump','JumpIfNot','Push'):assert int(n[2]) in boundaries
  if n[1]=='Context':
   _,a,b=d.spans[n[3][-1][0]];assert int(n[2].split()[0].split('=')[1])==b-a
  for c in n[3]:check(c)
 for n in nodes:check(n)
 p.changes[i]=raw[:loc]+struct.pack('<ii',d.p+d.extra,len(code))+code+tail
# Add a prefix with independent labels; relocate original ReceiveTick branches.
code=bytearray();vm=0;fix=[];labels={}
def emit(c):
 global vm
 code.extend(c);vm+=p.size(c)
def jump(label,cond=None):
 global vm
 code.append(7 if cond is not None else 6);fix.append((len(code),label));code.extend(bytes(4));vm+=5
 if cond is not None:emit(cond)
def label(n):labels[n]=vm
jump('end',valid('ControllerR'))
jump('create',valid('EkoroHeartMID'));jump('fade')
label('create')
emit(b'\x5f'+prop('EkoroHeartMID')+ctx(prop('ControllerR'),call('/Script/Engine.PrimitiveComponent.CreateDynamicMaterialInstance',b'\x25\x2a'),ref('EkoroHeartMID')))
label('fade');jump('end',valid('EkoroHeartMID'))
dt=b'\x00'+struct.pack('<i',p.ref('VRGG_Pawn_C.ReceiveTick.DeltaSeconds'))
emit(assign(math('FMax',fl(0),math('Subtract_FloatFloat',prop('EkoroHeartPulse'),math('Divide_FloatFloat',dt,fl(.16))))))
emit(update());label('end')
for pos,name in fix:struct.pack_into('<I',code,pos,labels[name])
info=script('ReceiveTick');old=bytearray(info[4]);d,_=p.parse(old)
for a in d.spans:
 if old[a] in (6,7,76):struct.pack_into('<I',old,a+1,struct.unpack_from('<I',old,a+1)[0]+vm)
save(info,bytes(code)+old)
# Redirect precisely the existing heart-effect spawn, keeping its original
# gameplay guards and all existing shot/hit branches unchanged.
info=script('Shot');old=info[4];d,nodes=p.parse(old)
def has_spawn(n):return (n[1]=='Call' and n[2].endswith('.SpawnEmitterAtLocation')) or any(has_spawn(c) for c in n[3])
matches=[n for n in nodes if n[1]=='Context' and has_spawn(n)]
assert len(matches)==1
n=matches[0];a=n[0];b,ms,me=d.spans[a];assert old[-1:]==b'\x53'
suffix=assign(fl(1));guard=valid('EkoroHeartMID');setvalue=update()
skip=info[3]-1+p.size(suffix)+5+p.size(guard)+p.size(setvalue)
suffix+=b'\x07'+struct.pack('<I',skip)+guard+setvalue+old[a:b]+b'\x06'+struct.pack('<I',me)+b'\x53'
new=old[:a]+b'\x06'+struct.pack('<I',info[3]-1)+b'\x0b'*(me-ms-5)+old[b:-1]+suffix
save(info,new)
p.save(root/'work/muzzle-pointer-v29/VRGG/Player/VRGG_Pawn')
(root/'outputs/HeartPulse_v29_build.json').write_text(json.dumps({'fade_seconds':.16,'linear_tint':[1,.82,.90],'base_blend':.85,'emissive_strength':.22,'shot_hook':'same guarded spawn as existing muzzle hearts','tick_prefix_vm':vm,'preserves':'v28 stabilization and story/menu fixes'},indent=2))
print('v29 shot/tick bytecode validated; heart-only pulse fades over 160ms')
