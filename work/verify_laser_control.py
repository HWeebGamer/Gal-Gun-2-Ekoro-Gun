"""Evaluate emitted laser state control and convergent transforms without Unreal."""
import struct,json,itertools,math,ast,argparse
from pathlib import Path
from cooked_patch import Package
args=argparse.ArgumentParser();args.add_argument('--bridge',action='store_true');args=args.parse_args()
version='v20' if args.bridge else 'v18'
root=Path(__file__).resolve().parent.parent
p=Package(root/f'work/muzzle-pointer-{version}/VRGG/Actors/PointerComponent.uasset')
report=json.loads((root/f'outputs/Laser_{version}_build.json').read_text())
raw=p.body(p.index('ExecuteUbergraph_PointerComponent'));loc=20+4*struct.unpack_from('<i',raw,16)[0];vm,sz=struct.unpack_from('<ii',raw,loc)
d,nodes=p.parse(raw[loc+8:loc+8+sz]);starts={d.spans[n[0]][1]:i for i,n in enumerate(nodes)}
def run(dual,cam,hidden,on,pressed,exists,target=(500,30,70)):
 state={'EkoroLaserBeam':'beam' if exists else None,'EkoroLaserEnabled':on,'DynamicMaterial':None,'HitLocation':target,'IsUsingDualMotionControllers':dual,'IsCameraControlAndReticleEnabled':cam,'ForceHideAimReticle':hidden};events=[];locals={}
 def ev(n):
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
  if op=='Context':return ev(cs[-1]) if ev(cs[0]) is not None else None
  if op in ('LetBool','LetObj'):
   dst=state if cs[0][1]=='Instance' else locals;dst[cs[0][2].split('.')[-1]]=ev(cs[1]);return
  if op in ('Math','Call'):
   args=[ev(c) for c in cs[:-1]]
   if name=='IsValid':return args[0] is not None
   if name=='GetOwner':return 'pawn'
   if name=='GetPlayerController':return 'controller'
   if name=='WasInputKeyJustPressed':assert args==[report['key']];return pressed
   if name=='Not_PreBool':return not args[0]
   if name=='K2_GetComponentLocation':return (0,0,0)
   if name=='GetUpVector':return (0,0,1)
   if name=='GetForwardVector':return (1,0,0)
   if name=='Add_VectorVector':return tuple(a+b for a,b in zip(*args))
   if name=='Subtract_VectorVector':return tuple(a-b for a,b in zip(*args))
   if name=='Multiply_VectorFloat':return tuple(a*args[1] for a in args[0])
   if name=='Divide_FloatFloat':return args[0]/args[1]
   if name=='VSize':return math.sqrt(sum(a*a for a in args[0]))
   if name=='MakeVector':return tuple(args)
   if name=='MakeRotFromZ':
    length=math.sqrt(sum(a*a for a in args[0]));return tuple(a/length for a in args[0])
   if name=='MakeTransform':return tuple(args)
   if name=='SpawnEmitterAtLocation':events.append(('spawn',args));return 'beam'
   if name=='K2_SetWorldTransform':events.append(('transform',args[0]));return
   if name=='SetVisibility':events.append(('visible',args[0]));return
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
 expected=(not on if pressed else on) if active else on
 assert state['EkoroLaserEnabled']==expected
 show=active and expected
 spawns=[e for e in events if e[0]=='spawn'];assert len(spawns)==int(show and not exists)
 visibility=[e[1] for e in events if e[0]=='visible']
 assert visibility==([show] if exists or show else [])
 transforms=[e[1] for e in events if e[0]=='transform'];assert len(transforms)==int(show)
 if show:
  center,axis,scale=transforms[0];source=(.15,0,-2.248535)
  first=tuple(c-a*scale[2]*50 for c,a in zip(center,axis));last=tuple(c+a*scale[2]*50 for c,a in zip(center,axis))
  assert all(abs(a-b)<1e-4 for a,b in zip(first,source))
  assert all(abs(a-b)<1e-4 for a,b in zip(last,target))
 return state,events
for case in itertools.product((False,True),repeat=6):run(*case)
for target in ((10,0,0),(0,5000,200),(-100,25,50)):run(True,True,False,False,True,False,target)
# New fields must belong to the component class and be linked as reflected children.
cls=p.body(p.index('PointerComponent_C'));base=list(p.tags(cls))[-1][-1]+8;count=struct.unpack_from('<i',cls,base+8)[0]
children=struct.unpack_from('<'+'i'*count,cls,base+12)
for name in ('EkoroLaserBeam','EkoroLaserEnabled'):
 i=p.index(name);assert i+1 in children and p.exports[i]['outer']==p.ref('PointerComponent_C')
 assert struct.unpack_from('<Q',p.body(i),16)[0]==0x2000
print('PASS: 64 state/input cases; component reuse; menu hiding; convergence at near/far/behind endpoints; reflected transient fields.')
