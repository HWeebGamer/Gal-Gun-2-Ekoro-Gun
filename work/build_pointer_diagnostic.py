"""v11: color the menu reticle from WidgetInteraction's actual hover state.
Adds three native getter imports; retains all existing package indices.
"""
import sys,struct,zlib,json
from pathlib import Path
root=Path(__file__).resolve().parent.parent
sys.argv=['decoder',str(root/'work/muzzle-pointer-v10/VRGG/Player/VRGG_Pawn.uasset')]
exec((root/'work/disassemble_blueprint.py').read_text().split('for e in exports:')[0])
original_names=len(names);original_imports=len(imports)
def hashes(s):
 h=0
 for ch in s.upper().encode('ascii'):
  v=((h^ch)&255)<<24
  for _ in range(8):v=((v<<1)^(0x04c11db7 if v&0x80000000 else 0))&0xffffffff
  h=(h>>8)^v
 return h&65535,zlib.crc32(s.encode('utf-32-le'))&65535
# Check hash implementation against names actually serialized by this game.
pos=name_offset;checked=0
for s in names:
 n=integer(pos);_,end=string(pos)
 if n>0 and s.isascii():
  assert struct.unpack_from('<HH',data,end)==hashes(s),(s,struct.unpack_from('<HH',data,end),hashes(s))
  checked+=1
 pos=end+4
old_name_table=data[name_offset:pos]
new_name_bytes=bytearray();new_import_bytes=bytearray()
def name_ref(s):
 if s not in names:
  names.append(s);raw=s.encode('ascii')+b'\0'
  new_name_bytes.extend(struct.pack('<i',len(raw))+raw+struct.pack('<HH',*hashes(s)))
 return struct.pack('<ii',names.index(s),0)
def ref(s):
 found=[i for i in range(-len(imports),len(exports)+1) if reference(i)==s]
 assert len(found)==1,s
 return found[0]
component=ref('/Script/UMG.WidgetInteractionComponent')
for name in ('GetHoveredWidgetComponent','IsOverHitTestVisibleWidget','IsOverInteractableWidget'):
 rec=name_ref('/Script/CoreUObject')+name_ref('Function')+struct.pack('<i',component)+name_ref(name)
 new_import_bytes.extend(rec);imports.append((name,component))
def prop(s):return b'\x01'+struct.pack('<i',ref('VRGG_Pawn_C.'+s))
def parse(code,validate=False):
 d=Decoder(code);nodes=[]
 while d.p<len(code):nodes.append(d.expr())
 if validate:
  boundaries={v[1] for v in d.spans.values()}
  def check(n):
   if n[1] in ('Jump','JumpIfNot','Push'):assert int(n[2]) in boundaries,(n[1],n[2])
   if n[1] in ('Context','ContextSilent'):
    expected=int(n[2].split()[0].split('=')[1]);_,a,b=d.spans[n[3][-1][0]];assert expected==b-a
   for child in n[3]:check(child)
  for n in nodes:check(n)
 return d.p+d.extra
def native(s,args=b'',math=False):return bytes([0x68 if math else 0x1c])+struct.pack('<i',ref(s))+args+b'\x16'
def context(obj,expr,result=0):return b'\x19'+obj+struct.pack('<Ii',parse(expr),result)+expr
def query(s,object_result=False):
 result=ref('VRGG_Pawn_C.WidgetInteraction' if object_result else 'VRGG_Pawn_C.TickCursor.CallFunc_IsValid_ReturnValue')
 return context(prop('WidgetInteraction'),native('/Script/UMG.WidgetInteractionComponent.'+s),result)
def valid(obj):return native('/Script/Engine.KismetSystemLibrary.IsValid',obj,True)
def color(r,g,b):
 c=b'\x2f'+struct.pack('<ii',ref('/Script/CoreUObject.LinearColor'),16)
 c+=b''.join(b'\x1e'+struct.pack('<f',v) for v in (r,g,b,1.))+b'\x30'
 return context(prop('ReticleWidget'),b'\x1b'+name_ref('Set Gun Sight Color')+c+b'\x16')
target=next(i for i,e in enumerate(exports) if e['name']=='TickCursor')
e=exports[target];start=e['offset']-header_size;raw=payload[start:start+e['size']]
loc=20+4*struct.unpack_from('<i',raw,16)[0];old_vm,size=struct.unpack_from('<ii',raw,loc)
old=raw[loc+8:loc+8+size];assert parse(old,True)==old_vm and old[-3:]==b'\x04\x0b\x53'
program=bytearray(old[:-3]);vm=old_vm-3;labels={};fixups=[]
def emit(code):
 global vm
 program.extend(code);vm+=parse(code)
def label(s):labels[s]=vm
def jump(s,condition=None):
 global vm
 program.append(7 if condition is not None else 6)
 fixups.append((len(program),s));program.extend(b'\0'*4);vm+=5
 if condition is not None:emit(condition)
notcamera=native('/Script/Engine.KismetMathLibrary.Not_PreBool',prop('IsCameraControlAndReticleEnabled'),True)
menu=native('/Script/Engine.KismetMathLibrary.BooleanOR',notcamera+prop('ForceHideAimReticle'),True)
jump('end',prop('IsUsingDualMotionControllers'));jump('end',menu)
jump('missing',valid(prop('WidgetInteraction')))
jump('no_component',valid(query('GetHoveredWidgetComponent',True)))
jump('no_path',query('IsOverHitTestVisibleWidget'))
jump('not_interactive',query('IsOverInteractableWidget'))
emit(color(0.,1.,0.));jump('end')
label('not_interactive');emit(color(0.,1.,1.));jump('end')
label('no_path');emit(color(1.,0.5,0.));jump('end')
label('no_component');emit(color(1.,0.,0.));jump('end')
label('missing');emit(color(1.,0.,1.))
label('end');emit(old[-3:])
for offset,label_name in fixups:struct.pack_into('<I',program,offset,labels[label_name])
assert parse(program,True)==vm
replacement=raw[:loc]+struct.pack('<ii',vm,len(program))+program+raw[loc+8+size:]
# Append relocated name/import tables; all original indices remain stable.
header=bytearray(data);new_name_offset=len(header);header.extend(old_name_table+new_name_bytes)
new_import_offset=len(header);header.extend(data[import_offset:import_offset+original_imports*28]+new_import_bytes)
new_header_size=len(header)
summary=24+integer(20)*20;_,folder_end=string(summary+4);fields=folder_end+4
struct.pack_into('<i',header,summary,new_header_size)
struct.pack_into('<ii',header,fields,len(names),new_name_offset)
struct.pack_into('<ii',header,fields+24,len(imports),new_import_offset)
gen_count=integer(fields+68);assert 0<=gen_count<=10
for i in range(gen_count):
 gen=fields+72+i*8
 assert integer(gen)==len(exports) and integer(gen+4)==original_names
 struct.pack_into('<i',header,gen+4,len(names))
result=bytearray();cursor=0
for i,e in sorted(enumerate(exports),key=lambda pair:pair[1]['offset']):
 start=e['offset']-header_size;assert start>=cursor
 result.extend(payload[cursor:start]);offset=new_header_size+len(result)
 body=replacement if i==target else payload[start:start+e['size']];result.extend(body)
 struct.pack_into('<qq',header,export_offset+i*104+28,len(body),offset)
 cursor=start+e['size']
result.extend(payload[cursor:])
needle=struct.pack('<q',header_size+len(payload)-4)
hits=[i for i in range(name_offset-7) if header[i:i+8]==needle];assert len(hits)==1
struct.pack_into('<q',header,hits[0],new_header_size+len(result)-4)
out=root/'work/muzzle-pointer-v11/VRGG/Player';out.mkdir(parents=True,exist_ok=True)
(out/'VRGG_Pawn.uasset').write_bytes(header);(out/'VRGG_Pawn.uexp').write_bytes(result)
report={'version':'v11 diagnostic','hashes_verified':checked,'new_native_getters':3,'old_VM':old_vm,'new_VM':vm,'colors':{'magenta':'WidgetInteraction missing','red':'No hovered widget component reported','orange':'Widget component reported, no hit-test-visible Slate widget','cyan':'Hit-test-visible Slate widget, not interactable','green':'Interactable widget reported'}}
(root/'outputs/MenuPointer_v11_build.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
