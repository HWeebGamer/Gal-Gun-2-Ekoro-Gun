"""Check v15 shot guards and unchanged gameplay exports using emitted bytecode."""
import itertools,struct
from pathlib import Path
from cooked_patch import Package
root=Path(__file__).resolve().parent.parent
p=Package(root/'work/muzzle-pointer-v15/VRGG/Player/VRGG_Pawn.uasset')
old=Package(root/'work/muzzle-pointer-v11/VRGG/Player/VRGG_Pawn.uasset')
changed=[e['name'] for i,e in enumerate(p.exports) if p.body(i)!=old.body(i)]
assert changed==['Shot'],changed
def script(pkg):
 raw=pkg.body(pkg.index('Shot'));loc=20+4*struct.unpack_from('<i',raw,16)[0];vm,sz=struct.unpack_from('<ii',raw,loc)
 return vm,raw[loc+8:loc+8+sz]
vm,original=script(old);_,code=script(p);d,nodes=p.parse(code)
starts={d.spans[n[0]][1]:i for i,n in enumerate(nodes)}
od,on=old.parse(original);resume=od.spans[on[0][0]][2]
for dual,enabled,hidden,reticle,valid in itertools.product((False,True),repeat=5):
 state={'IsUsingDualMotionControllers':dual,'IsCameraControlAndReticleEnabled':enabled,'ForceHideAimReticle':hidden,'ReticleStatus':int(reticle),'PointerComponent':'pointer' if valid else None};spawn=[]
 def ev(n):
  _,op,detail,cs=n
  if op=='Instance':return state[detail.split('.')[-1]]
  if op=='Object':return detail
  if op=='Self':return 'pawn'
  if op in ('True','False'):return op=='True'
  if op=='Byte':return int(detail)
  if op=='Vector':return detail
  if op=='LetBool':return
  if op=='Context':return ev(cs[-1]) if ev(cs[0]) is not None else None
  if op in ('Math','Call'):
   args=[ev(c) for c in cs[:-1]];fn=detail.split('.')[-1]
   if fn=='Not_PreBool':return not args[0]
   if fn=='NotEqual_ByteByte':return args[0]!=args[1]
   if fn=='IsValid':return args[0] is not None
   if fn=='K2_GetComponentLocation':return 'muzzle_position'
   if fn=='K2_GetComponentRotation':return 'muzzle_rotation'
   if fn=='SpawnEmitterAtLocation':spawn.append(args);return
  raise AssertionError((op,detail))
 pc=starts[vm-1]
 for _ in range(20):
  n=nodes[pc]
  if n[1]=='Jump':assert int(n[2])==resume;break
  if n[1]=='JumpIfNot':pc=pc+1 if ev(n[3][0]) else starts[int(n[2])]
  else:ev(n);pc+=1
 else:raise AssertionError('Shot trampoline did not resume')
 assert len(spawn)==int(dual and enabled and not hidden and reticle and valid)
 if spawn:assert spawn[0][2:4]==['muzzle_position','muzzle_rotation'] and spawn[0][-1] is True
print('PASS: 32 firing guard combinations; muzzle transform; auto-destroy; only Shot export changed.')
