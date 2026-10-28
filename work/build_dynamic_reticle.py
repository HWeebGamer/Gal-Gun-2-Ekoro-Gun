"""v14: distance taper and eased enemy-target shrink in the pointer scale update."""
import sys, struct, json, zlib
from pathlib import Path
root=Path(__file__).resolve().parent.parent
sys.argv=['decoder',str(root/'work/muzzle-pointer-v13/VRGG/Actors/PointerComponent.uasset')]
exec((root/'work/disassemble_blueprint.py').read_text().split('for e in exports:')[0])
original_names=len(names);original_imports=len(imports)
def hashes(s):
 h=0
 for ch in s.upper().encode('ascii'):
  v=((h^ch)&255)<<24
  for _ in range(8):v=((v<<1)^(0x04c11db7 if v&0x80000000 else 0))&0xffffffff
  h=(h>>8)^v
 return h&65535,zlib.crc32(s.encode('utf-32-le'))&65535
pos=name_offset
for s in names:
 n=integer(pos);_,end=string(pos)
 if n>0 and s.isascii():assert struct.unpack_from('<HH',data,end)==hashes(s)
 pos=end+4
old_name_table=data[name_offset:pos];new_names=bytearray();new_imports=bytearray()
def name_ref(s):
 if s not in names:
  names.append(s);b=s.encode()+b'\0';new_names.extend(struct.pack('<i',len(b))+b+struct.pack('<HH',*hashes(s)))
 return struct.pack('<ii',names.index(s),0)
def ref(s):
 matches=[i for i in range(-len(imports),len(exports)+1) if reference(i)==s]
 assert len(matches)==1,s
 return matches[0]
def add(s,kind,outer):
 full=reference(outer)+'.'+s if outer else s
 for i in range(-len(imports),0):
  if reference(i)==full:return i
 new_imports.extend(name_ref('/Script/CoreUObject')+name_ref(kind)+struct.pack('<i',outer)+name_ref(s))
 imports.append((s,outer));return -len(imports)
mathlib=ref('/Script/Engine.KismetMathLibrary')
for fn in ('Divide_FloatFloat','Add_FloatFloat','FInterpTo','VSize','Not_PreBool'):
 add(fn,'Function',mathlib)
add('K2_GetComponentScale','Function',ref('/Script/Engine.SceneComponent'))
pawnclass=ref('/Game/VRGG/Player/VRGG_Pawn.VRGG_Pawn_C')
for field in ('IsUsingDualMotionControllers','IsCameraControlAndReticleEnabled','ForceHideAimReticle'):
 add(field,'BoolProperty',pawnclass)
enemy_classes=[]
for package,cls in [('/Game/VRGG/AI/GAL/GAL','GAL_C'),('/Game/VRGG/AI/MiniKurona/MiniKuronaPawn','MiniKuronaPawn_C'),('/Game/VRGG/AI/MiniRisu/MiniRisuPawn','MiniRisuPawn_C')]:
 enemy_classes.append(add(cls,'BlueprintGeneratedClass',add(package,'Package',0)))
def parse(code):
 d=Decoder(code);nodes=[]
 while d.p<len(code):nodes.append(d.expr())
 return d,nodes
def size(code):
 d,_=parse(code);return d.p+d.extra
def prop(s):return b'\x01'+struct.pack('<i',ref('PointerComponent_C.'+s))
def local(s):return b'\x00'+struct.pack('<i',ref('PointerComponent_C.ExecuteUbergraph_PointerComponent.'+s))
def native(s,args=b'',math=False):return bytes([0x68 if math else 0x1c])+struct.pack('<i',ref(s))+args+b'\x16'
def math(s,*args):return native('/Script/Engine.KismetMathLibrary.'+s,b''.join(args),True)
def fl(v):return b'\x1e'+struct.pack('<f',v)
def context(obj,expr,result=0):return b'\x19'+obj+struct.pack('<Ii',size(expr),result)+expr
def valid(obj):return native('/Script/Engine.KismetSystemLibrary.IsValid',obj,True)
def assign(expr):
 r=ref('PointerComponent_C.ExecuteUbergraph_PointerComponent.CallFunc_GetFloatValue_ReturnValue')
 return b'\x0f'+struct.pack('<i',r)+b'\x00'+struct.pack('<i',r)+expr
target=next(i for i,e in enumerate(exports) if e['name']=='ExecuteUbergraph_PointerComponent')
e=exports[target];start=e['offset']-header_size;raw=payload[start:start+e['size']]
loc=20+4*struct.unpack_from('<i',raw,16)[0];old_vm,disk=struct.unpack_from('<ii',raw,loc)
old=raw[loc+8:loc+8+disk];d,nodes=parse(old);assert size(old)==old_vm and old[-3:]==b'\x04\x0b\x53'
node=next(n for n in nodes if n[1]=='Let' and n[2]=='PointerComponent_C.ExecuteUbergraph_PointerComponent.CallFunc_GetFloatValue_ReturnValue')
a=node[0];b,ms,me=d.spans[a];original_assignment=old[a:b]
# Leave all existing VM addresses and external event entry points unchanged.
# The scale expression jumps to a tail block, which returns to its old successor.
redirect=b'\x06'+struct.pack('<I',old_vm-1)+b'\x0b'*(me-ms-5)
program=bytearray(old[:a]+redirect+old[b:-1]);vm=old_vm-1
labels={};fixups=[]
def emit(code):
 global vm
 program.extend(code);vm+=size(code)
def label(s):labels[s]=vm
def jump(s,condition=None):
 global vm
 program.append(7 if condition is not None else 6);fixups.append((len(program),s));program.extend(b'\0'*4);vm+=5
 if condition is not None:emit(condition)
emit(original_assignment)
owner=b'\x2e'+struct.pack('<i',pawnclass)+native('/Script/Engine.ActorComponent.GetOwner')
def pawnflag(s):
 r=ref('/Game/VRGG/Player/VRGG_Pawn.VRGG_Pawn_C.'+s)
 return context(owner,b'\x01'+struct.pack('<i',r),r)
jump('return',valid(owner))
jump('return',pawnflag('IsUsingDualMotionControllers'))
jump('return',pawnflag('IsCameraControlAndReticleEnabled'))
jump('return',math('Not_PreBool',pawnflag('ForceHideAimReticle')))
# Save baseline curve size into its existing local before applying a taper.
taper=math('FClamp',math('Divide_FloatFloat',fl(1200),math('Add_FloatFloat',prop('HitDistance'),fl(1000))),fl(.35),fl(1))
emit(assign(math('Multiply_FloatFloat',local('CallFunc_GetFloatValue_ReturnValue'),taper)))
# Refresh the hit actor from this frame's final trace, not a prior-frame local.
hitnode=next(n for n in nodes if n[1]=='Context' and n[3][-1][1]=='Call' and n[3][-1][2]=='/Script/Engine.GameplayStatics.BreakHitResult' and any(c[2].endswith('.CallFunc_BreakHitResult_HitActor3') for c in n[3][-1][3]))
emit(old[hitnode[0]:d.spans[hitnode[0]][0]])
for i,cls in enumerate(enemy_classes):
 condition=valid(b'\x2e'+struct.pack('<i',cls)+local('CallFunc_BreakHitResult_HitActor3'))
 jump('next'+str(i),condition)
 emit(assign(math('Multiply_FloatFloat',local('CallFunc_GetFloatValue_ReturnValue'),fl(.8))))
 jump('smooth');label('next'+str(i))
label('smooth')
# AimReticle is uniformly scaled by the original transform path. Read its
# previous world scale to ease toward the new size without accumulating scale.
vector_result=ref('PointerComponent_C.ExecuteUbergraph_PointerComponent.CallFunc_Conv_FloatToVector_ReturnValue')
current=context(prop('AimReticle'),native('/Script/Engine.SceneComponent.K2_GetComponentScale'),vector_result)
current=math('Multiply_FloatFloat',math('VSize',current),fl(3**-.5))
emit(assign(math('FInterpTo',current,local('CallFunc_GetFloatValue_ReturnValue'),local('K2Node_Event_DeltaSeconds'),fl(12))))
label('return');emit(b'\x06'+struct.pack('<I',me));emit(b'\x53')
for offset,name in fixups:struct.pack_into('<I',program,offset,labels[name])
nd,nn=parse(program);assert nd.p+nd.extra==vm
boundaries={s[1] for s in nd.spans.values()}
def check(n):
 if n[1] in ('Jump','JumpIfNot','Push'):assert int(n[2]) in boundaries
 if n[1] in ('Context','ContextSilent'):
  _,lo,hi=nd.spans[n[3][-1][0]];assert int(n[2].split()[0].split('=')[1])==hi-lo
 for child in n[3]:check(child)
for n in nn:check(n)
replacement=raw[:loc]+struct.pack('<ii',vm,len(program))+program+raw[loc+8+disk:]
header=bytearray(data);new_name_offset=len(header);header.extend(old_name_table+new_names)
new_import_offset=len(header);header.extend(data[import_offset:import_offset+original_imports*28]+new_imports)
hs=len(header);summary=24+integer(20)*20;_,folder_end=string(summary+4);fields=folder_end+4
struct.pack_into('<i',header,summary,hs)
struct.pack_into('<ii',header,fields,len(names),new_name_offset)
struct.pack_into('<ii',header,fields+24,len(imports),new_import_offset)
for i in range(integer(fields+68)):
 gen=fields+72+i*8;assert integer(gen)==len(exports) and integer(gen+4)==original_names
 struct.pack_into('<i',header,gen+4,len(names))
out=bytearray();cursor=0
for i,e in sorted(enumerate(exports),key=lambda p:p[1]['offset']):
 start=e['offset']-header_size;out.extend(payload[cursor:start]);offset=hs+len(out)
 body=replacement if i==target else payload[start:start+e['size']];out.extend(body)
 struct.pack_into('<qq',header,export_offset+i*104+28,len(body),offset);cursor=start+e['size']
out.extend(payload[cursor:]);needle=struct.pack('<q',header_size+len(payload)-4)
hits=[i for i in range(name_offset-7) if header[i:i+8]==needle];assert len(hits)==1
struct.pack_into('<q',header,hits[0],hs+len(out)-4)
dest=root/'work/muzzle-pointer-v14/VRGG/Actors/PointerComponent';dest.parent.mkdir(parents=True,exist_ok=True)
dest.with_suffix('.uasset').write_bytes(header);dest.with_suffix('.uexp').write_bytes(out)
report={'old_VM':old_vm,'new_VM':vm,'tail_VM':old_vm-1,'resume_VM':me,'enemy_multiplier':.8,'interp_speed':12,'taper':'clamp(1200/(distance_cm+1000), 0.35, 1)','gameplay_only':True,'max_distance_cm':5000,'added_imports':len(imports)-original_imports}
(root/'outputs/DynamicReticle_v14_build.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
