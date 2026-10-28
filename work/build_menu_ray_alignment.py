"""v12: replace the VR menu's fixed world ray with the barrel pointer rotation."""
import sys,struct,json
from pathlib import Path
root=Path(__file__).resolve().parent.parent
sys.argv=['decoder',str(root/'UmodelSaved/Game/VRGG/Widgets/VRGG_Widget.uasset')]
exec((root/'work/disassemble_blueprint.py').read_text().split('for e in exports:')[0])
def ref(s):
 matches=[i for i in range(-len(imports),len(exports)+1) if reference(i)==s]
 assert len(matches)==1,s
 return matches[0]
def parse(code):
 d=Decoder(code);nodes=[]
 while d.p<len(code):nodes.append(d.expr())
 return d,nodes
def context(obj,expr,result):
 d,_=parse(expr)
 return b'\x19'+obj+struct.pack('<Ii',d.p+d.extra,result)+expr
target=next(i for i,e in enumerate(exports) if e['name']=='Mouse Update')
e=exports[target];start=e['offset']-header_size;raw=payload[start:start+e['size']]
loc=20+4*struct.unpack_from('<i',raw,16)[0];vm,size=struct.unpack_from('<ii',raw,loc)
code=raw[loc+8:loc+8+size];d,nodes=parse(code);assert d.p+d.extra==vm
assigns=[n for n in nodes if n[1]=='Let' and n[2].startswith('VRGG_Widget_C.Mouse Update.CallFunc_')]
assert [n[2].split('.')[-1] for n in assigns]==['CallFunc_MakeVector_ReturnValue','CallFunc_MakeVector_ReturnValue2','CallFunc_FindLookAtRotation_ReturnValue']
a=assigns[0][0];b=d.spans[assigns[-1][0]][0]
budget=d.spans[assigns[-1][0]][2]-d.spans[a][1]
rot=ref('VRGG_Widget_C.Mouse Update.CallFunc_FindLookAtRotation_ReturnValue')
pawn=b'\x00'+struct.pack('<i',ref('VRGG_Widget_C.Mouse Update.K2Node_DynamicCast_AsVRGG_Pawn'))
pointer_ref=ref('/Game/VRGG/Player/VRGG_Pawn.VRGG_Pawn_C.PointerComponent')
pointer=context(pawn,b'\x01'+struct.pack('<i',pointer_ref),pointer_ref)
getter=b'\x1c'+struct.pack('<i',ref('/Script/Engine.SceneComponent.K2_GetComponentRotation'))+b'\x16'
replacement=b'\x0f'+struct.pack('<i',rot)+b'\x00'+struct.pack('<i',rot)+context(pointer,getter,rot)
rd,_=parse(replacement);used=rd.p+rd.extra;assert used<=budget
new=code[:a]+replacement+b'\x0b'*(budget-used)+code[b:]
nd,nn=parse(new);assert nd.p+nd.extra==vm
boundaries={s[1] for s in nd.spans.values()}
def validate(n):
 if n[1] in ('Jump','JumpIfNot','Push'):assert int(n[2]) in boundaries
 if n[1] in ('Context','ContextSilent'):
  _,lo,hi=nd.spans[n[3][-1][0]]
  assert int(n[2].split()[0].split('=')[1])==hi-lo
 for child in n[3]:validate(child)
for n in nn:validate(n)
body=raw[:loc]+struct.pack('<ii',vm,len(new))+new+raw[loc+8+size:]
header=bytearray(data);out=bytearray();cursor=0
for i,x in sorted(enumerate(exports),key=lambda pair:pair[1]['offset']):
 p=x['offset']-header_size;out.extend(payload[cursor:p]);offset=header_size+len(out)
 chunk=body if i==target else payload[p:p+x['size']];out.extend(chunk)
 struct.pack_into('<qq',header,export_offset+104*i+28,len(chunk),offset)
 cursor=p+x['size']
out.extend(payload[cursor:])
needle=struct.pack('<q',header_size+len(payload)-4)
hits=[i for i in range(name_offset-7) if header[i:i+8]==needle];assert len(hits)<=1
for i in hits:struct.pack_into('<q',header,i,header_size+len(out)-4)
dest=root/'work/muzzle-pointer-v12/VRGG/Widgets/VRGG_Widget';dest.parent.mkdir(parents=True,exist_ok=True)
dest.with_suffix('.uasset').write_bytes(header);dest.with_suffix('.uexp').write_bytes(out)
report={'changed_function':'VRGG_Widget.Mouse Update','source':'original extracted asset','VM_size_preserved':vm,'replacement_VM_size':used,'replaced_VM_size':budget,'all_other_export_payloads_unchanged':True,'global_cursor_gate':'original','trigger_handling':'unchanged v11','diagnostic_colors':'retained v11'}
(root/'outputs/MenuPointer_v12_build.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
