"""Build reversible cooked Blueprint override using the original package tables.
No original game files are modified. Script offsets are validated in VM bytes.
"""
import sys,struct,json,hashlib
from pathlib import Path
workspace=Path(__file__).resolve().parent.parent
native_menu_confirm='--native-menu-confirm' in sys.argv
menu_ray_fix='--menu-ray-fix' in sys.argv or native_menu_confirm
menu_interaction='--menu-interaction' in sys.argv or menu_ray_fix
menu_visibility='--menu-visibility' in sys.argv or menu_interaction
sys.argv=['disassembler',str(workspace/'UmodelSaved/Game/VRGG/Player/VRGG_Pawn.uasset')]
exec((workspace/'work/disassemble_blueprint.py').read_text().split('for e in exports:')[0])
def decode(b):
 d=Decoder(b)
 nodes=[]
 while d.p<len(b): nodes.append(d.expr())
 boundaries={span[1] for span in d.spans.values()}
 def check(node):
  start,op,detail,children=node
  if op in ('Jump','JumpIfNot','Push'):
   assert int(detail) in boundaries,(start,op,detail)
  if op in ('Context','ContextSilent'):
   expected=int(detail.split()[0].split('=')[1]);end,begin,finish=d.spans[children[-1][0]]
   assert expected==finish-begin,(start,expected,finish-begin)
  for child in children: check(child)
 for node in nodes: check(node)
 return d
def index(name):
 matches=[i+1 for i,e in enumerate(exports) if reference(i+1)==name]
 assert len(matches)==1,name
 return matches[0]
def script(e):
 raw=payload[e['offset']-header_size:e['offset']-header_size+e['size']]
 loc=20+4*struct.unpack_from('<i',raw,16)[0]
 mem,size=struct.unpack_from('<ii',raw,loc)
 b=raw[loc+8:loc+8+size];d=decode(b)
 assert d.p+d.extra==mem
 return raw,loc,b,d
replacements={};report={}
def replace(name,new):
 i=index('VRGG_Pawn_C.'+name)-1;e=exports[i]
 raw,loc,old,d=script(e); nd=decode(new)
 replacements[i]=raw[:loc]+struct.pack('<ii',nd.p+nd.extra,len(new))+new+raw[loc+8+len(old):]
 report[name]={'old_disk':len(old),'new_disk':len(new),'old_VM':d.p+d.extra,'new_VM':nd.p+nd.extra}
raw,loc,b,d=script(exports[index('VRGG_Pawn_C.AttachPointerToHMD')-1])
# Original first attach expression; replace camera-manager parent with right mesh.
attach=bytearray(b[0x20:0x5d])
assert b[0x39]==0x19 and b[0x47]==0x01
attach[0x39-0x20:0x4c-0x20]=b'\x01'+struct.pack('<i',index('VRGG_Pawn_C.ControllerR'))
# Context skip accounts for shorter parent expression: 61 -> 39 VM bytes.
struct.pack_into('<I',attach,0x2c-0x20,39)
# Keep camera-attached collision box behavior and the existing transform setter.
transform=bytearray(b[0xba:0x111])
# UE mesh-space muzzle, cm. Center of muzzle face, slightly in front of it.
# UModel PSK/glTF exports mirror Y relative to the raw UE vertex buffer.
# Verified against the actual cooked .uexp position floats.
muzzle=(-0.358717,-6.8,-0.751465)
struct.pack_into('<3f',transform,0xca-0xba,*muzzle)
struct.pack_into('<3f',transform,0xd7-0xba,0.0,-90.0,0.0)
vr=bytes(attach)+b[0x5d:0xba]+bytes(transform)+b'\x04\x0b'
v=decode(vr)
prefix=b'\x07'+struct.pack('<I',14+v.p+v.extra)+b'\x01'+struct.pack('<i',index('VRGG_Pawn_C.IsUsingDualMotionControllers'))
replace('AttachPointerToHMD',prefix+vr+b)
# The existing setter is in the dual-controller branch. Keep ALL original VM
# jump targets stable by replacing exactly its VM footprint with call + NOPs.
raw,loc,b,d=script(exports[index('VRGG_Pawn_C.HandleInput')-1])
end,ms,me=d.spans[0x9c6]
assert end==0x9e6
call=b'\x1b'+struct.pack('<ii',names.index('AttachPointerToHMD'),0)+b'\x16'
assert decode(call).p+decode(call).extra==14
replace('HandleInput',b[:0x9c6]+call+b'\x0b'*(me-ms-14)+b[end:])
# Angle consumers should also use the new shared barrel ray.
raw,loc,b,d=script(exports[index('VRGG_Pawn_C.GetDualMotionControllersCursorAngle')-1])
old=b'\x01'+struct.pack('<i',index('VRGG_Pawn_C.VivePointer'))
new=b'\x01'+struct.pack('<i',index('VRGG_Pawn_C.PointerComponent'))
assert b.count(old)==2
replace('GetDualMotionControllersCursorAngle',b.replace(old,new))
if menu_visibility:
 # Standalone wrappers avoid changing the ubergraph's externally referenced
 # entry offsets. Restore the menu's camera/input gate after showing its sight.
 def mem(code):
  decoder=Decoder(code)
  while decoder.p<len(code): decoder.expr()
  return decoder.p+decoder.extra
 def prop(name): return b'\x01'+struct.pack('<i',index('VRGG_Pawn_C.'+name))
 def virtual(name,args=b''):
  return b'\x1b'+struct.pack('<ii',names.index(name),0)+args+b'\x16'
 def native(name,args=b''):
  refs=[i for i in range(-len(imports),len(exports)+1) if reference(i)==name]
  assert len(refs)==1,name
  return b'\x1c'+struct.pack('<i',refs[0])+args+b'\x16'
 def context(obj,expr):
  return b'\x19'+obj+struct.pack('<Ii',mem(expr),0)+expr
 def boolean(name,value): return b'\x14'+prop(name)+(b'\x27' if value else b'\x28')
 def guard(condition,body,base=0):
  size=5+mem(condition)+mem(body)
  return b'\x07'+struct.pack('<I',base+size)+condition+body
 not_camera=b'\x68'+native('/Script/Engine.KismetMathLibrary.Not_PreBool',prop('IsCameraControlAndReticleEnabled'))[1:]
 core=boolean('IsCameraControlAndReticleEnabled',True)+virtual('SetReticleStatus',b'\x24\x01')+boolean('IsCameraControlAndReticleEnabled',False)
 # Explicit hide requests also gate SetReticleStatus. Temporarily clear that
 # flag only around the call, then restore it for the game's later transitions.
 hidden_core=boolean('ForceHideAimReticle',False)+core+boolean('ForceHideAimReticle',True)
 show_base=14+14+5+mem(not_camera)
 normal_start=show_base+14+mem(hidden_core)+5
 both_end=normal_start+mem(core)
 show=b'\x07'+struct.pack('<I',normal_start)+prop('ForceHideAimReticle')+hidden_core+b'\x06'+struct.pack('<I',both_end)+core
 visible=context(prop('ReticleWidgetComponent'),native('/Script/Engine.SceneComponent.SetVisibility',b'\x27\x27'))
 visible+=context(prop('ReticleWidgetComponent'),native('/Script/Engine.SceneComponent.SetHiddenInGame',b'\x28\x28'))
 visible+=context(prop('ReticleWidget'),virtual('SetVisibility',b'\x24'+(b'\x03' if menu_ray_fix else b'\x04')))
 show+=visible
 attach_call=virtual('AttachPointerToHMD')
 inner=guard(not_camera,show,14+mem(attach_call))
 extra=b''
 if menu_ray_fix:
  # Menus can hide the sight without disabling camera input. Preserve both
  # flags, but allow the sight to appear in this separate state too.
  camera_and_hidden=b'\x68'+native('/Script/Engine.KismetMathLibrary.BooleanAND',prop('IsCameraControlAndReticleEnabled')+prop('ForceHideAimReticle'))[1:]
  show_hidden=boolean('ForceHideAimReticle',False)+virtual('SetReticleStatus',b'\x24\x01')+boolean('ForceHideAimReticle',True)+visible
  extra=guard(camera_and_hidden,show_hidden,14+mem(attach_call)+mem(inner))
  extra+=context(prop('ReticleWidgetComponent'),virtual('SetCollisionEnabled',b'\x24\x00'))
  extra+=context(prop('ReticleWidget'),virtual('SetVisibility',b'\x24\x03'))
  extra+=context(prop('WidgetInteraction'),native('/Script/Engine.ActorComponent.SetTickableWhenPaused',b'\x27'))
 prefix=guard(prop('IsUsingDualMotionControllers'),attach_call+inner+extra)
 raw,loc,b,d=script(exports[index('VRGG_Pawn_C.ReceiveTick')-1])
 replace('ReceiveTick',prefix+b)
 # Menu rays need an opaque cursor even where the gameplay color logic has
 # no target. Preserve gameplay colors when its camera/reticle gate is enabled.
 color_ref=[i for i in range(-len(imports),0) if reference(i)=='/Script/CoreUObject.LinearColor']
 assert len(color_ref)==1
 white=b'\x2f'+struct.pack('<ii',color_ref[0],16)+b''.join(b'\x1e'+struct.pack('<f',x) for x in (1.,1.,1.,1.))+b'\x30'
 color=context(prop('ReticleWidget'),virtual('Set Gun Sight Color',white))
 raw,loc,b,d=script(exports[index('VRGG_Pawn_C.TickCursor')-1])
 assert b[-3:]==b'\x04\x0b\x53'
 menu_color=not_camera
 if menu_ray_fix:
  menu_color=b'\x68'+native('/Script/Engine.KismetMathLibrary.BooleanOR',not_camera+prop('ForceHideAimReticle'))[1:]
 base=mem(b[:-3]);inner=guard(menu_color,color,base+14)
 suffix=guard(prop('IsUsingDualMotionControllers'),inner,base)
 replace('TickCursor',b[:-3]+suffix+b[-3:])
 report['menu_visibility']='ReceiveTick refresh outside HandleInput gate; temporary visibility enable; opaque menu cursor'
 if menu_interaction and not native_menu_confirm:
  for phase in ('Pressed','Released'):
   raw,loc,b,d=script(exports[index('VRGG_Pawn_C.Menu_Decide_'+phase)-1])
   # Prefix VR dispatch and relocate the original function-relative jumps.
   dispatch=virtual('Menu_Mouse_Decide_'+phase)+b'\x04\x0b'
   prefix=guard(prop('IsUsingDualMotionControllers'),dispatch)
   shift=mem(prefix)
   adjusted=bytearray(b)
   for start,(end,ms,me) in d.spans.items():
    if b[start] in (6,7,76):
     struct.pack_into('<I',adjusted,start+1,struct.unpack_from('<I',b,start+1)[0]+shift)
   replace('Menu_Decide_'+phase,prefix+adjusted)
  report['menu_input']='Dual-controller confirm uses existing mouse pointer press/release; original confirm path preserved otherwise'
header=bytearray(data);result=bytearray();cursor=0
for i,e in sorted(enumerate(exports),key=lambda pair:pair[1]['offset']):
 start=e['offset']-header_size
 assert start>=cursor
 result.extend(payload[cursor:start]);new_offset=header_size+len(result)
 body=replacements.get(i,payload[start:start+e['size']]);result.extend(body)
 struct.pack_into('<qq',header,export_offset+i*104+28,len(body),new_offset)
 cursor=start+e['size']
result.extend(payload[cursor:])
# Summary BulkDataStartOffset points to the end of package payload before tag.
old_bulk=header_size+len(payload)-4;new_bulk=header_size+len(result)-4
needle=struct.pack('<q',old_bulk)
hits=[i for i in range(name_offset-7) if header[i:i+8]==needle]
assert len(hits)<=1,hits
for i in hits: struct.pack_into('<q',header,i,new_bulk)
out=workspace/('work/muzzle-pointer-v8/VRGG/Player' if native_menu_confirm else 'work/muzzle-pointer-v7/VRGG/Player' if menu_ray_fix else 'work/muzzle-pointer-v6/VRGG/Player' if menu_interaction else 'work/muzzle-pointer-v5/VRGG/Player' if menu_visibility else 'work/muzzle-pointer/VRGG/Player');out.mkdir(parents=True,exist_ok=True)
(out/'VRGG_Pawn.uasset').write_bytes(header)
(out/'VRGG_Pawn.uexp').write_bytes(result)
report['muzzle_cm']=muzzle;report['rotation_pitch_yaw_roll']=[0,-90,0]
report['bulk_offset_updated']=hits
report['original_sha256']=hashlib.sha256(data+payload).hexdigest()
if menu_ray_fix: report['ray_fix']='Cover ForceHide with camera enabled; restore flags; reticle HitTestInvisible=3 and collision disabled'
if native_menu_confirm: report['menu_input']='Original controller confirm/release functions restored byte-for-byte; no mouse rerouting'
(workspace/('outputs/MuzzlePointer_v8_build.json' if native_menu_confirm else 'outputs/MuzzlePointer_v7_build.json' if menu_ray_fix else 'outputs/MuzzlePointer_v6_build.json' if menu_interaction else 'outputs/MuzzlePointer_v5_build.json' if menu_visibility else 'outputs/MuzzlePointer_build.json')).write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
