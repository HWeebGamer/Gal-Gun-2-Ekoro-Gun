"""v10: accept real hover events without changing global cursor/menu state."""
import sys,struct,json
from pathlib import Path
root=Path(__file__).resolve().parent.parent
decoder_source=(root/'work/disassemble_blueprint.py').read_text().split('for e in exports:')[0]
report=[]
def load(relative):
 sys.argv=['decoder',str(root/relative)]
 ns={'__file__':str(root/'work/disassemble_blueprint.py')}
 exec(decoder_source,ns)
 return ns
def save(ns,replacements,relative):
 header=bytearray(ns['data']);payload=ns['payload'];result=bytearray();cursor=0;hs=ns['header_size']
 for i,e in sorted(enumerate(ns['exports']),key=lambda pair:pair[1]['offset']):
  start=e['offset']-hs;assert start>=cursor
  result.extend(payload[cursor:start]);offset=hs+len(result)
  body=replacements.get(i,payload[start:start+e['size']]);result.extend(body)
  struct.pack_into('<qq',header,ns['export_offset']+104*i+28,len(body),offset)
  cursor=start+e['size']
 result.extend(payload[cursor:])
 needle=struct.pack('<q',hs+len(payload)-4)
 hits=[i for i in range(ns['name_offset']-7) if header[i:i+8]==needle];assert len(hits)<=1
 for i in hits:struct.pack_into('<q',header,i,hs+len(result)-4)
 out=root/'work/muzzle-pointer-v10'/relative;out.parent.mkdir(parents=True,exist_ok=True)
 out.with_suffix('.uasset').write_bytes(header);out.with_suffix('.uexp').write_bytes(result)
for rel,functions in [
 ('VRGG/Widgets/WidgetControl/VRGG_SelectControl_Widget',{'Button Hovered','Button Unhovered'}),
 ('VRGG/Widgets/Base/Title/VRGG_TitleMenu_Widget',{'ExecuteUbergraph_VRGG_TitleMenu_Widget'}),
]:
 ns=load('UmodelSaved/Game/'+rel+'.uasset');changes={}
 for i,e in enumerate(ns['exports']):
  if e['name'] not in functions:continue
  start=e['offset']-ns['header_size'];raw=ns['payload'][start:start+e['size']]
  loc=20+4*struct.unpack_from('<i',raw,16)[0];vm,size=struct.unpack_from('<ii',raw,loc)
  code=raw[loc+8:loc+8+size];d=ns['Decoder'](code);nodes=[]
  while d.p<len(code):nodes.append(d.expr())
  assert d.p+d.extra==vm
  targets=[n for n in nodes if n[1]=='Virtual' and n[2]=='Is Show Mouse Cursor'];assert len(targets)==1
  n=targets[0];start=n[0];end,ms,me=d.spans[start]
  arg=n[3][0];assert arg[1]=='Local'
  assignment=b'\x14'+code[arg[0]:arg[0]+5]+b'\x27' # local output=true
  # LetBool + variable pointer + True occupies 11 runtime bytes.
  new=code[:start]+assignment+b'\x0b'*(me-ms-11)+code[end:]
  d2=ns['Decoder'](new);parsed=[]
  while d2.p<len(new):parsed.append(d2.expr())
  assert d2.p+d2.extra==vm
  boundaries={x[1] for x in d2.spans.values()}
  def check(node):
   if node[1] in ('Jump','JumpIfNot','Push'):assert int(node[2]) in boundaries
   for child in node[3]:check(child)
  for node in parsed:check(node)
  changes[i]=raw[:loc]+struct.pack('<ii',vm,len(new))+new+raw[loc+8+size:]
  report.append({'asset':rel,'function':e['name'],'VM_size_preserved':vm})
 assert len(changes)==len(functions)
 save(ns,changes,rel)
# Reuse the confirmed v9 pawn and change only the reticle's default draw order.
ns=load('work/muzzle-pointer-v8/VRGG/Player/VRGG_Pawn.uasset')
i=next(i for i,e in enumerate(ns['exports']) if e['name']=='ReticleWidgetComponent_GEN_VARIABLE')
e=ns['exports'][i];start=e['offset']-ns['header_size'];raw=ns['payload'][start:start+e['size']]
c=0
while True:
 tag=c;name=ns['fname'](raw,c);c+=8
 if name=='None':break
 assert name!='TranslucencySortPriority'
 kind=ns['fname'](raw,c);size=struct.unpack_from('<i',raw,c+8)[0];c+=16
 if kind=='StructProperty':c+=24
 elif kind=='BoolProperty':c+=1
 elif kind in ('ByteProperty','EnumProperty','ArrayProperty'):c+=8
 elif kind in ('MapProperty','SetProperty'):c+=16 if kind=='MapProperty' else 8
 guid=raw[c];c+=1+(16 if guid else 0);c+=size
def fname(name):return struct.pack('<ii',ns['names'].index(name),0)
prop=fname('TranslucencySortPriority')+fname('IntProperty')+struct.pack('<iiBi',4,0,0,10000)
save(ns,{i:raw[:tag]+prop+raw[tag:]},'VRGG/Player/VRGG_Pawn')
report.append({'asset':'VRGG/Player/VRGG_Pawn','component':e['name'],'TranslucencySortPriority':10000})
(root/'outputs/MenuHover_v10_build.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
