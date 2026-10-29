"""Evaluate emitted laser state control and convergent transforms without Unreal."""
import struct,json,itertools,math,ast,argparse
from pathlib import Path
from cooked_patch import Package
args=argparse.ArgumentParser();args.add_argument('--bridge',action='store_true');args.add_argument('--always-on',action='store_true');args.add_argument('--aligned',action='store_true');args.add_argument('--visible',action='store_true');args.add_argument('--dot',action='store_true');args=args.parse_args()
if args.dot:args.visible=True
if args.visible:args.aligned=True
if args.aligned:args.always_on=True
version='v24' if args.dot else 'v23' if args.visible else 'v22' if args.aligned else 'v21' if args.always_on else ('v20' if args.bridge else 'v18')
root=Path(__file__).resolve().parent.parent
p=Package(root/f'work/muzzle-pointer-{version}/VRGG/Actors/PointerComponent.uasset')
report=json.loads((root/f'outputs/Laser_{version}_build.json').read_text())
raw=p.body(p.index('ExecuteUbergraph_PointerComponent'));loc=20+4*struct.unpack_from('<i',raw,16)[0];vm,sz=struct.unpack_from('<ii',raw,loc)
d,nodes=p.parse(raw[loc+8:loc+8+sz]);starts={d.spans[n[0]][1]:i for i,n in enumerate(nodes)}
if args.always_on:
 def verify_stored_transform(n):
  assert not (n[1] in ('Call','Math') and n[2].endswith('.WasInputKeyJustPressed'))
  if args.aligned and n[1]=='Math' and n[2].endswith('.MakeRotFromZ'):
   assert n[3][0][1]=='Local' and n[3][0][2].endswith('.CallFunc_Subtract_VectorVector_ReturnValue')
  if n[1]=='Context' and n[3][0][2] in ('PointerComponent_C.EkoroLaserBeam','PointerComponent_C.EkoroLaserDot'):
   call=n[3][-1]
   if call[2].endswith('.K2_SetWorldTransform'):
    assert call[3][0][1]=='Local'
    assert call[3][0][2].endswith('.CallFunc_MakeTransform_ReturnValue')
  for child in n[3]:verify_stored_transform(child)
 for n in nodes:verify_stored_transform(n)
def run(dual,cam,hidden,on,pressed,exists,target=(500,30,70),origin=(0,0,0),beam_active=True,dot_exists=None):
 state={'EkoroLaserBeam':'beam' if exists else None,'EkoroLaserEnabled':on,'DynamicMaterial':None,'HitLocation':target,'IsUsingDualMotionControllers':dual,'IsCameraControlAndReticleEnabled':cam,'ForceHideAimReticle':hidden};events=[];locals={}
 if dot_exists is None:dot_exists=exists
 state.update(EkoroLaserDot='dot' if dot_exists else None,AimReticle='reticle')
 current_component=None
 def ev(n):
  nonlocal current_component
  _,op,detail,cs=n;name=detail.split('.')[-1]
  if op=='Instance':return state[name]
  if op=='Local':return locals.get(name)
  if op in ('Float','Byte','Int'):return float(detail)
  if op=='Zero':return 0
  if op=='Self':return 'pointer'
  if op=='Object':return detail
  if op=='Name':return detail
  if op=='Struct':return ev(cs[0])
  if op in ('Vector','Rotation'):return ast.literal_eval(detail)
  if op in ('True','False'):return op=='True'
  if op=='Cast':return 'pawn'
  if op=='Context':
   obj=ev(cs[0]);previous=current_component;current_component=obj
   try:return ev(cs[-1]) if obj is not None else None
   finally:current_component=previous
  if op in ('Let','LetBool','LetObj'):
   dst=state if cs[0][1]=='Instance' else locals;dst[cs[0][2].split('.')[-1]]=ev(cs[1]);return
  if op in ('Math','Call'):
   args=[ev(c) for c in cs[:-1]]
   if name=='IsActive':return beam_active if (dot_exists if current_component=='dot' else exists) else True
   if name=='Activate':events.append(('activate',args,current_component));return
   if name=='IsValid':return args[0] is not None
   if name=='GetOwner':return 'pawn'
   if name=='GetPlayerController':return 'controller'
   if name=='WasInputKeyJustPressed':assert args==[report['key']];return pressed
   if name=='Not_PreBool':return not args[0]
   if name=='K2_GetComponentLocation':return origin
   if name=='K2_GetComponentScale':return (.05,.05,.05)
   if name=='GetUpVector':return (0,0,1)
   if name=='GetForwardVector':return (1,0,0)
   if name=='Add_VectorVector':return tuple(a+b for a,b in zip(*args))
   if name=='Subtract_VectorVector':return tuple(a-b for a,b in zip(*args))
   if name=='Multiply_VectorFloat':return tuple(a*args[1] for a in args[0])
   if name=='Multiply_FloatFloat':return args[0]*args[1]
   if name=='Divide_FloatFloat':return args[0]/args[1]
   if name=='VSize':return math.sqrt(sum(a*a for a in args[0]))
   if name=='MakeVector':return tuple(args)
   if name=='MakeRotFromZ':
    length=math.sqrt(sum(a*a for a in args[0]));return tuple(a/length for a in args[0])
   if name=='MakeTransform':return tuple(args)
   if name=='SpawnEmitterAtLocation':events.append(('spawn',args));return 'dot' if 'P_EkoroLaserDot' in args[1] else 'beam'
   if name=='K2_SetWorldTransform':events.append(('transform',args[0],current_component));return
   if name=='SetVisibility':events.append(('visible',args[0],current_component));return
  raise AssertionError((op,detail))
 pc=starts[report['tail_VM']]
 for _ in range(70):
  n=nodes[pc]
  if n[1] in ('Jump','JumpIfNot'):
   take=n[1]=='Jump' or not ev(n[3][0]);dest=int(n[2])
   if take and dest==report['resume_VM']:break
   pc=starts[dest] if take else pc+1
  else:ev(n);pc+=1
 else:raise AssertionError('Laser tail failed to return')
 active=dual and cam and not hidden
 expected=on if args.always_on else ((not on if pressed else on) if active else on)
 assert state['EkoroLaserEnabled']==expected
 show=active and (args.always_on or expected)
 assert len([e for e in events if e[0]=='activate' and e[2]=='beam'])==int(args.visible and show and exists and not beam_active)
 spawns=[e for e in events if e[0]=='spawn' and 'P_EkoroLaserDot' not in e[1][1]];assert len(spawns)==int(show and not exists)
 visibility=[e[1] for e in events if e[0]=='visible' and e[2]=='beam']
 assert visibility==([show] if exists or show else [])
 transforms=[e[1] for e in events if e[0]=='transform' and e[2]=='beam'];assert len(transforms)==int(show)
 if show:
  center,axis,scale=transforms[0];source=tuple(a+b for a,b in zip(origin,(.15,0,-2.248535)))
  first=tuple(c-a*scale[2]*50 for c,a in zip(center,axis));last=tuple(c+a*scale[2]*50 for c,a in zip(center,axis))
  assert all(abs(a-b)<1e-4 for a,b in zip(first,source))
  assert all(abs(a-b)<1e-4 for a,b in zip(last,target))
 if args.dot:
  assert len([e for e in events if e[0]=='spawn' and 'P_EkoroLaserDot' in e[1][1]])==int(show and not dot_exists)
  assert len([e for e in events if e[0]=='activate' and e[2]=='dot'])==int(show and dot_exists and not beam_active)
  dot_visibility=[e[1] for e in events if e[0]=='visible' and e[2]=='dot']
  assert dot_visibility==([show] if dot_exists or show else [])
  dots=[e[1] for e in events if e[0]=='transform' and e[2]=='dot']
  assert len(dots)==int(show)
  if show:
   position,axis,scale=dots[0]
   assert all(abs(a-b)<1e-5 for a,b in zip(position,(target[0]+.1,target[1],target[2])))
   assert all(abs(a-b)<1e-5 for a,b in zip(axis,(1,0,0)))
   assert all(abs(a-b)<1e-6 for a,b in zip(scale,(.006,.006,.0001)))
 return state,events
for case in itertools.product((False,True),repeat=6):run(*case)
for target in ((10,0,0),(0,5000,200),(-100,25,50)):run(True,True,False,False,True,False,target)
for origin in ((1200,-800,170),(-3000,500,80)):
 run(True,True,False,False,False,False,tuple(a+b for a,b in zip(origin,(500,30,70))),origin)
if args.visible:
 for case in itertools.product((False,True),repeat=6):run(*case,beam_active=False)
if args.dot:
 for case in itertools.product((False,True),repeat=6):run(*case,beam_active=False,dot_exists=not case[-1])
# New fields must belong to the component class and be linked as reflected children.
cls=p.body(p.index('PointerComponent_C'));base=list(p.tags(cls))[-1][-1]+8;count=struct.unpack_from('<i',cls,base+8)[0]
children=struct.unpack_from('<'+'i'*count,cls,base+12)
for name in (('EkoroLaserBeam','EkoroLaserEnabled','EkoroLaserDot') if args.dot else ('EkoroLaserBeam','EkoroLaserEnabled')):
 i=p.index(name);assert i+1 in children and p.exports[i]['outer']==p.ref('PointerComponent_C')
 assert struct.unpack_from('<Q',p.body(i),16)[0]==0x2000
print('PASS: 64 state/input cases; component reuse; menu hiding; convergence at near/far/behind endpoints; reflected transient fields.')
