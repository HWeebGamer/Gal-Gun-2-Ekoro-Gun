"""Execute patched hover bytecode and cursor tail against synthetic menu states."""
import itertools,json,struct
from pathlib import Path
from cooked_patch import Package
root=Path(__file__).resolve().parent.parent
def load(path,fn):
 p=Package(path);raw=p.body(p.index(fn));loc=20+4*struct.unpack_from('<i',raw,16)[0];vm,size=struct.unpack_from('<ii',raw,loc)
 d,nodes=p.parse(raw[loc+8:loc+8+size]);assert d.p+d.extra==vm
 return p,d,{d.spans[n[0]][1]:n for n in nodes}

def execute(d,nodes,state,local,start=0,story=False,component=None):
 stack=[];pc=start
 def ev(n):
  _,op,detail,cs=n;name=detail.split('.')[-1]
  if op=='Instance':
   if name=='bHiddenInGame':return component['hidden']
   return state[name]
  if op in ('Local','Out'):return local.get(name)
  if op in ('Int','Byte'):return int(detail)
  if op=='Float':return float(detail)
  if op in ('True','False'):return op=='True'
  if op=='Null':return None
  if op=='Object':return detail
  if op=='Cast':return 'story' if story and ev(cs[0]) else None
  if op=='Struct':return tuple(ev(c) for c in cs[:-1])
  if op=='Context':return ev(cs[-1]) if ev(cs[0]) is not None else None
  if op in ('Let','LetBool','LetObj'):
   target=state if cs[0][1]=='Instance' else local;target[cs[0][2].split('.')[-1]]=ev(cs[1]);return
  if op=='Nothing':return
  if op in ('Virtual','Math','Call'):
   if name=='Array_Get':local[cs[2][2].split('.')[-1]]=ev(cs[0])[ev(cs[1])];return
   if name=='Get Talk Window Widget':local[cs[1][2].split('.')[-1]]='widget'+str(ev(cs[0]));return
   if name=='Make Other Button Unselected':state['cleared_others']=state['SelectingWindowIndex'];return
   a=[ev(c) for c in cs[:-1]]
   if name=='Array_Length':return len(a[0])
   if name=='Not_PreBool':return not a[0]
   if name=='Less_IntInt':return a[0]<a[1]
   if name=='BooleanAND':return a[0] and a[1]
   if name=='EqualEqual_ObjectObject':return a[0]==a[1]
   if name=='NotEqual_IntInt':return a[0]!=a[1]
   if name=='Add_IntInt':return a[0]+a[1]
   if name=='IsValid':return a[0] is not None
   if name=='IsVisible':return component['visible']
   if name=='SetVisibility':
    if op=='Call':component['visible']=a[0]
    else:component['widget_visibility']=a[0]
    return
   if name=='SetHiddenInGame':component['hidden']=a[0];return
   if name=='Set Gun Sight Color':component['color']=a[0];return
  raise AssertionError(n)
 for _ in range(1000):
  n=nodes[pc];op=n[1];nextpc=d.spans[n[0]][2]
  if op=='Return':return
  if op=='Push':stack.append(int(n[2]))
  elif op=='Pop' or (op=='PopIfNot' and not ev(n[3][0])):
   assert stack;nextpc=stack.pop()
  elif op=='Jump' or (op=='JumpIfNot' and not ev(n[3][0])):nextpc=int(n[2])
  elif op not in ('PopIfNot','JumpIfNot'):ev(n)
  pc=nextpc
 raise AssertionError('Script did not terminate')

path=root/'work/muzzle-pointer-v26/VRGG/Widgets/Demo/VRGG_TalkSelectActor.uasset'
p,d,nodes=load(path,'Talk Window Hovered');cases=0
for count in (2,3):
 for enabled in itertools.product((False,True),repeat=count):
  for hovered in range(count):
   for cursor_allowed in (False,True):
    for previous in range(-1,count):
     state={'EnableCursorControl':cursor_allowed,'CurrentTalkSelectWindowArray':list(range(count)),'EnableSelectArray':enabled,'SelectingWindowIndex':previous}
     execute(d,nodes,state,{'Select Widget':'widget'+str(hovered)})
     assert state['SelectingWindowIndex']==(hovered if cursor_allowed and enabled[hovered] else previous)
     cases+=1
# Only the scoped actor hover function changed.
old=Package(root.parent/'UmodelSaved/Game/VRGG/Widgets/Demo/VRGG_TalkSelectActor.uasset')
assert p.imports==old.imports
for i,e in enumerate(old.exports):
 if e['name']!='Talk Window Hovered':assert p.body(i)==old.body(i)

p,d,nodes=load(root/'work/muzzle-pointer-v26/VRGG/Player/VRGG_Pawn.uasset','TickCursor')
report=json.loads((root/'outputs/Story_v26_build.json').read_text());start=report['cursor_tail_VM']
for visible,hidden in itertools.product((False,True),repeat=2):
 state={'IsUsingDualMotionControllers':True,'ActiveWidgetActor':'actor','ReticleWidgetComponent':'component','ReticleWidget':'widget',**{f:False for f in report['fields']}}
 component={'visible':visible,'hidden':hidden}
 for _ in range(2):execute(d,nodes,state,{},start,True,component)
 assert component['visible'] and not component['hidden'] and component['color']==(1.,)*4
 state['ActiveWidgetActor']=None
 execute(d,nodes,state,{},start,False,component)
 assert component['visible']==visible and component['hidden']==hidden and not state['EkoroStoryCursorOverride']
for dual,story in ((False,True),(True,False),(False,False)):
 state={'IsUsingDualMotionControllers':dual,'ActiveWidgetActor':'actor','ReticleWidgetComponent':'component','ReticleWidget':'widget',**{f:False for f in report['fields']}}
 component={'visible':False,'hidden':True};execute(d,nodes,state,{},start,story,component)
 assert component=={'visible':False,'hidden':True}
print(f'PASS: {cases} story hover/index cases; cursor entry/repeat/exit restoration; non-story and non-VR isolation; other actor exports unchanged.')
