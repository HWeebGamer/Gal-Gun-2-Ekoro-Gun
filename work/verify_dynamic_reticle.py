"""Evaluate emitted v14 scale bytecode for range, target, menu, and easing cases."""
import sys,struct,json,math,itertools
from pathlib import Path
root=Path(__file__).resolve().parent.parent
sys.argv=['decoder',str(root/'work/muzzle-pointer-v14/VRGG/Actors/PointerComponent.uasset')]
exec((root/'work/disassemble_blueprint.py').read_text().split('for e in exports:')[0])
report=json.loads((root/'outputs/DynamicReticle_v14_build.json').read_text())
e=next(e for e in exports if e['name']=='ExecuteUbergraph_PointerComponent')
raw=payload[e['offset']-header_size:e['offset']-header_size+e['size']]
loc=20+4*struct.unpack_from('<i',raw,16)[0];vm,length=struct.unpack_from('<ii',raw,loc)
d=Decoder(raw[loc+8:loc+8+length]);nodes=[]
while d.p<len(d.b):nodes.append(d.expr())
starts={d.spans[n[0]][1]:i for i,n in enumerate(nodes)}
scale='CallFunc_GetFloatValue_ReturnValue'
def run(distance,current,dt,enemy,dual=True,enabled=True,hidden=False):
 state={'HitDistance':distance,'ScaleCurve':'curve','AimReticle':'reticle','HitResult':'hit',
        'IsUsingDualMotionControllers':dual,'IsCameraControlAndReticleEnabled':enabled,'ForceHideAimReticle':hidden}
 locals={'K2Node_Event_DeltaSeconds':dt,'CallFunc_BreakHitResult_HitActor3':'stale_enemy'}
 def ev(n):
  _,op,detail,cs=n;short=detail.split('.')[-1]
  if op=='Local':return locals.get(short)
  if op=='Instance':return state[short]
  if op=='Object':return detail
  if op=='Float':return float(detail)
  if op=='Cast':return 'pawn' if detail.endswith('VRGG_Pawn_C') else (enemy if enemy and detail.endswith(enemy) else None)
  if op=='Context':return ev(cs[-1]) if ev(cs[0]) is not None else None
  if op=='Let':locals[cs[0][2].split('.')[-1]]=ev(cs[1]);return
  if op in ('Call','Math'):
   if short=='BreakHitResult':
    for arg in cs[1:-1]:locals[arg[2].split('.')[-1]]=enemy if 'HitActor' in arg[2] else None
    return
   args=[ev(c) for c in cs[:-1]]
   if short=='GetFloatValue':return distance # Original curve keys are (0,0),(500,500),(100000,100000).
   if short=='GetOwner':return 'pawn'
   if short=='IsValid':return args[0] is not None
   if short=='Not_PreBool':return not args[0]
   if short=='Multiply_FloatFloat':return args[0]*args[1]
   if short=='Add_FloatFloat':return sum(args)
   if short=='Divide_FloatFloat':return args[0]/args[1]
   if short=='FClamp':return max(args[1],min(args[2],args[0]))
   if short=='K2_GetComponentScale':return (current,)*3
   if short=='VSize':return math.sqrt(sum(v*v for v in args[0]))
   if short=='FInterpTo':return args[0]+(args[1]-args[0])*max(0,min(1,args[2]*args[3]))
  raise AssertionError((op,detail))
 pc=starts[report['tail_VM']]
 for _ in range(100):
  n=nodes[pc]
  if n[1] in ('Jump','JumpIfNot'):
   taken=n[1]=='Jump' or not ev(n[3][0]);target=int(n[2])
   if taken and target==report['resume_VM']:return locals[scale]
   pc=starts[target] if taken else pc+1
  else:ev(n);pc+=1
 raise AssertionError('Nonterminating scale tail')
cases=0
for distance,enemy,dual,enabled,hidden in itertools.product((50,200,500,1000,2000,5000),(None,'wall','GAL_C','MiniKuronaPawn_C','MiniRisuPawn_C'),(False,True),(False,True),(False,True)):
 current=distance;dt=1/90
 result=run(distance,current,dt,enemy,dual,enabled,hidden)
 active=dual and enabled and not hidden
 factor=max(.35,min(1,1200/(distance+1000)))
 multiplier=.8 if enemy in ('GAL_C','MiniKuronaPawn_C','MiniRisuPawn_C') else 1
 desired=distance*factor*multiplier
 expected=current+(desired-current)*dt*12 if active else distance
 assert math.isclose(result,expected,rel_tol=1e-6),(distance,enemy,result,expected)
 cases+=1
# Repeated frames must converge and recover without cumulative shrinking.
for fps in (45,72,90,120):
 distance=1000;value=distance
 for _ in range(fps):value=run(distance,value,1/fps,'GAL_C')
 assert math.isclose(value,480,rel_tol=1e-4)
 for _ in range(fps):value=run(distance,value,1/fps,None)
 assert math.isclose(value,600,rel_tol=1e-4)
# Verify only the intended function payload changes from v13.
old_ns={'__file__':str(root/'work/read_pawn_properties.py')}
sys.argv=['reader',str(root/'work/muzzle-pointer-v13/VRGG/Actors/PointerComponent.uasset')]
exec((root/'work/read_pawn_properties.py').read_text().split("print('TABLES'")[0],old_ns)
changed=[]
for new,old in zip(exports,old_ns['exports']):
 a=new['offset']-header_size;b=old['offset']-old_ns['header_size']
 if payload[a:a+new['size']]!=old_ns['payload'][b:b+old['size']]:changed.append(new['name'])
assert changed==['ExecuteUbergraph_PointerComponent'],changed
print(f'PASS: {cases} scale cases; easing/recovery at 45/72/90/120 Hz; only pointer scale function payload changed.')
