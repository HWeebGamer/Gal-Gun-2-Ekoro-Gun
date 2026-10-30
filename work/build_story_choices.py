"""v26: scoped story-choice hover acceptance and reversible VR cursor visibility."""
import json
import struct
from pathlib import Path
from cooked_patch import Package
root=Path(__file__).resolve().parent.parent
def script(p,fn):
 i=p.index(fn);raw=p.body(i);loc=20+4*struct.unpack_from('<i',raw,16)[0];vm,size=struct.unpack_from('<ii',raw,loc)
 return i,raw,loc,vm,raw[loc+8:loc+8+size],raw[loc+8+size:]
def validate(p,code):
 d,nodes=p.parse(code);boundaries={s[1] for s in d.spans.values()}
 def check(n):
  if n[1] in ('Jump','JumpIfNot','Push'):assert int(n[2]) in boundaries
  if n[1]=='Context':assert int(n[2].split()[0].split('=')[1])==p.size(code[n[3][-1][0]:d.spans[n[3][-1][0]][0]])
  for c in n[3]:check(c)
 for n in nodes:check(n)
 return d.p+d.extra

p=Package(root.parent/'UmodelSaved/Game/VRGG/Widgets/Demo/VRGG_TalkSelectActor.uasset')
i,raw,loc,vm,code,tail=script(p,'Talk Window Hovered');d,nodes=p.parse(code)
matches=[n for n in nodes if n[1]=='Context' and n[3][-1][1:3]==('Virtual','Is Show Mouse Cursor')]
assert len(matches)==1
n=matches[0];a=n[0];b,ms,me=d.spans[a];out=n[3][-1][3][0];assert out[1]=='Local'
replacement=b'\x14'+code[out[0]:out[0]+5]+b'\x27'
new=code[:a]+replacement+b'\x0b'*(me-ms-p.size(replacement))+code[b:]
assert validate(p,new)==vm
p.changes[i]=raw[:loc]+struct.pack('<ii',vm,len(new))+new+tail
p.save(root/'work/muzzle-pointer-v26/VRGG/Widgets/Demo/VRGG_TalkSelectActor')

p=Package(root/'work/muzzle-pointer-v15/VRGG/Player/VRGG_Pawn.uasset')
owner=p.ref('VRGG_Pawn_C')
fields=['EkoroStoryCursorOverride','EkoroStoryCursorWasVisible','EkoroStoryCursorWasHidden']
for name in fields:p.add_property(name,'IsUsingDualMotionControllers',owner)
story=p.add('VRGG_TalkSelectActor_C','BlueprintGeneratedClass',p.add('/Game/VRGG/Widgets/Demo/VRGG_TalkSelectActor','Package'))
scene=p.ref('/Script/Engine.SceneComponent')
p.add('IsVisible','Function',scene);hidden=p.add('bHiddenInGame','BoolProperty',scene)
def prop(s):return b'\x01'+struct.pack('<i',p.ref('VRGG_Pawn_C.'+s))
def call(s,args=b'',math=False):return bytes([0x68 if math else 0x1c])+struct.pack('<i',p.ref(s))+args+b'\x16'
def context(obj,expr,result=0):return b'\x19'+obj+struct.pack('<Ii',p.size(expr),result)+expr
def valid(obj):return call('/Script/Engine.KismetSystemLibrary.IsValid',obj,True)
def virtual(name,args):return b'\x1b'+p.name(name)+args+b'\x16'
component=prop('ReticleWidgetComponent')
def scene_call(fn,args=b''):return context(component,call('/Script/Engine.SceneComponent.'+fn,args))
def assign(name,value):return b'\x14'+prop(name)+value
i,raw,loc,oldvm,old,tail=script(p,'TickCursor')
assert old[-3:]==b'\x04\x0b\x53'
code=bytearray(old[:-3]);vm=oldvm-3;labels={};fix=[]
def emit(c):
 global vm
 code.extend(c);vm+=p.size(c)
def jump(label,condition=None):
 global vm
 code.append(7 if condition is not None else 6);fix.append((len(code),label));code.extend(b'\0'*4);vm+=5
 if condition is not None:emit(condition)
def label(name):labels[name]=vm
jump('restore',prop('IsUsingDualMotionControllers'))
jump('restore',valid(b'\x2e'+struct.pack('<i',story)+prop('ActiveWidgetActor')))
jump('end',valid(component));jump('end',valid(prop('ReticleWidget')))
jump('capture',prop(fields[0]));jump('show')
label('capture')
emit(assign(fields[1],scene_call('IsVisible')))
emit(assign(fields[2],context(component,b'\x01'+struct.pack('<i',hidden),hidden)))
emit(assign(fields[0],b'\x27'))
label('show')
emit(scene_call('SetVisibility',b'\x27\x28'));emit(scene_call('SetHiddenInGame',b'\x28\x28'))
emit(context(prop('ReticleWidget'),virtual('SetVisibility',b'\x24\x03')))
color=b'\x2f'+struct.pack('<ii',p.ref('/Script/CoreUObject.LinearColor'),16)+b''.join(b'\x1e'+struct.pack('<f',1.) for _ in range(4))+b'\x30'
emit(context(prop('ReticleWidget'),virtual('Set Gun Sight Color',color)));jump('end')
label('restore');jump('end',prop(fields[0]));jump('clear',valid(component))
emit(scene_call('SetVisibility',prop(fields[1])+b'\x28'));emit(scene_call('SetHiddenInGame',prop(fields[2])+b'\x28'))
label('clear');emit(assign(fields[0],b'\x28'))
label('end');emit(b'\x04\x0b\x53')
for offset,name in fix:struct.pack_into('<I',code,offset,labels[name])
assert validate(p,code)==vm
p.changes[i]=raw[:loc]+struct.pack('<ii',vm,len(code))+code+tail
p.save(root/'work/muzzle-pointer-v26/VRGG/Player/VRGG_Pawn')
(root/'outputs/Story_v26_build.json').write_text(json.dumps({'cursor_tail_VM':oldvm-3,'cursor_end_VM':labels['end'],'fields':fields},indent=2))
print('Built scoped story hover and reversible VR cursor override; gameplay and laser logic retained.')
