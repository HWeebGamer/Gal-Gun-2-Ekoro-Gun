"""Validate v11's scope and evaluate its emitted color decision bytecode."""
import sys,struct,json,itertools
from pathlib import Path
root=Path(__file__).resolve().parent.parent
sys.argv=['d',str(root/'work/muzzle-pointer-v11/VRGG/Player/VRGG_Pawn.uasset')]
exec((root/'work/disassemble_blueprint.py').read_text().split('for e in exports:')[0])
new_exports=exports;new_payload=payload;new_header_size=header_size
target=next(e for e in exports if e['name']=='TickCursor')
raw=payload[target['offset']-header_size:target['offset']-header_size+target['size']]
loc=20+4*struct.unpack_from('<i',raw,16)[0];size=struct.unpack_from('<i',raw,loc+4)[0]
d=Decoder(raw[loc+8:loc+8+size]);nodes=[]
while d.p<len(d.b):nodes.append(d.expr())
starts={d.spans[n[0]][1]:i for i,n in enumerate(nodes)}
report=json.loads((root/'outputs/MenuPointer_v11_build.json').read_text())
begin=starts[report['old_VM']-3]
cases=0
for dual,menu,exists,hover,hit,interactive in itertools.product([False,True],repeat=6):
 colors=[]
 state={'IsUsingDualMotionControllers':dual,'IsCameraControlAndReticleEnabled':not menu,'ForceHideAimReticle':False,'WidgetInteraction':'component' if exists else None,'ReticleWidget':'sight'}
 def ev(n):
  _,op,detail,cs=n
  if op=='Instance':return state[detail.split('.')[-1]]
  if op=='Float':return float(detail)
  if op=='Struct':return tuple(ev(c) for c in cs[:-1])
  if op=='Context':return ev(cs[-1]) if ev(cs[0]) is not None else None
  if op in ('Math','Call'):
   args=[ev(c) for c in cs[:-1]]
   name=detail.split('.')[-1]
   if name=='Not_PreBool':return not args[0]
   if name=='BooleanOR':return any(args)
   if name=='IsValid':return args[0] is not None
   if name=='GetHoveredWidgetComponent':return 'widget' if hover else None
   if name=='IsOverHitTestVisibleWidget':return hit
   if name=='IsOverInteractableWidget':return interactive
   raise AssertionError(name)
  if op=='Virtual' and detail=='Set Gun Sight Color':colors.append(ev(cs[0]));return
  raise AssertionError((op,detail))
 i=begin
 while nodes[i][1]!='Return':
  n=nodes[i]
  if n[1]=='Jump':i=starts[int(n[2])];continue
  if n[1]=='JumpIfNot':
   if not ev(n[3][0]):i=starts[int(n[2])];continue
  else:ev(n)
  i+=1
 expected=[] if not dual or not menu else [(1.,0.,1.,1.) if not exists else (1.,0.,0.,1.) if not hover else (1.,.5,0.,1.) if not hit else (0.,1.,1.,1.) if not interactive else (0.,1.,0.,1.)]
 assert colors==expected,(state,hover,hit,interactive,colors,expected)
 cases+=1
# Reload only the table reader in an independent namespace for byte comparison.
sys.argv=['r',str(root/'work/muzzle-pointer-v10/VRGG/Player/VRGG_Pawn.uasset')]
ns={'__file__':str(root/'work/read_pawn_properties.py')}
exec((root/'work/read_pawn_properties.py').read_text().split("print('TABLES'")[0],ns)
changes=[]
for a,b in zip(ns['exports'],new_exports):
 assert a['name']==b['name']
 old=ns['payload'][a['offset']-ns['header_size']:a['offset']-ns['header_size']+a['size']]
 new=new_payload[b['offset']-new_header_size:b['offset']-new_header_size+b['size']]
 if old!=new:changes.append(a['name'])
assert changes==['TickCursor'],changes
print(f'PASS: {cases} diagnostic state combinations; only TickCursor export changed from v10.')
