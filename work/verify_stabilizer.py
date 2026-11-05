"""Execute emitted filter prefix against mocked UE rotation/component calls."""
import math,struct
from pathlib import Path
from cooked_patch import Package
p=Package(Path(__file__).resolve().parents[1]/'work/muzzle-pointer-v28/VRGG/Player/VRGG_Pawn.uasset')
raw=p.body(p.index('ReceiveTick'));loc=20+4*struct.unpack_from('<i',raw,16)[0];_,sz=struct.unpack_from('<ii',raw,loc)
code=raw[loc+8:loc+8+sz];d,nodes=p.parse(code)
import json
limit=json.loads((Path(__file__).resolve().parents[1]/'outputs/Stabilizer_v28_build.json').read_text())['prefix_vm']
starts={d.spans[n[0]][1]:i for i,n in enumerate(nodes)}
def delta(a,b):return (a-b+180)%360-180
state={};world=0.;tracked=True;dt=1/90
def run(rawangle,menu=False,tracking=True,seconds=1/90):
 global world,tracked,dt
 world=rawangle;tracked=tracking;dt=seconds
 state.update(ControllerR='gun',MotionControllerR='tracker',PointerComponent='pointer',IsUsingDualMotionControllers=True,IsCameraControlAndReticleEnabled=not menu,ForceHideAimReticle=False,EkoroStoryCursorOverride=False)
 def ev(n):
  _,op,name,ch=n;key=name.split('.')[-1]
  if op=='Instance':return 0. if key=='RelativeRotation' else state.get(key,False)
  if op=='Local':assert key=='DeltaSeconds';return dt
  if op=='Float':return float(name)
  if op in ('True','False'):return op=='True'
  if op=='Self':return 'pawn'
  if op in ('Let','LetBool'):
   state[ch[0][2].split('.')[-1]]=ev(ch[1]);return
  if op=='Context':return ev(ch[-1])
  if op in ('Call','Math'):
   args=[ev(c) for c in ch if c[1]!='EndParams']
   if key in ('AddTickPrerequisiteActor','AddTickPrerequisiteComponent'):return
   if key=='K2_SetRelativeRotation':return
   if key=='K2_GetComponentRotation':return rawangle
   if key=='K2_SetWorldRotation':
    globals()['world']=args[0];return
   if key=='IsValid':return bool(args[0])
   if key=='IsTracked':return tracked
   if key=='Not_PreBool':return not args[0]
   if key=='LessEqual_FloatFloat':return args[0]<=args[1]
   if key=='Greater_FloatFloat':return args[0]>args[1]
   if key=='EqualEqual_RotatorRotator':return abs(delta(args[0],args[1]))<=args[2]
   if key=='Exp':return math.exp(args[0])
   if key=='Divide_FloatFloat':return args[0]/args[1]
   if key=='Subtract_FloatFloat':return args[0]-args[1]
   if key=='RLerp':assert args[3];return args[0]+delta(args[1],args[0])*args[2]
  raise AssertionError((op,name))
 i=0
 while d.spans[nodes[i][0]][1]<limit:
  n=nodes[i]
  if n[1]=='Jump' or (n[1]=='JumpIfNot' and not ev(n[3][0])):i=starts[int(n[2])]
  else:
   if n[1]!='JumpIfNot':ev(n)
   i+=1
 return world
run(0);out=run(.3);assert 0<out<.3
assert run(15)==15 # deliberate turn
assert run(15.3,menu=True)==15.3
assert run(15.4)==15.4 # menu recovery seeds
assert run(15.6,tracking=False)==15.6
assert run(15.7)==15.7
assert run(15.9,seconds=.2)==15.9
state.clear();run(179.9);assert abs(delta(run(-179.9),179.9))<.2
results=[]
for hz in (60,72,90,120):
 state.clear();run(0,seconds=1/hz)
 for _ in range(hz):value=run(.5,seconds=1/hz)
 assert abs(value-.5)<1e-8
 results.append(value)
state.clear();run(0)
raws=[];filtered=[]
for i in range(300):
 a=.15*math.sin(2*math.pi*12*i/90);raws.append(a);filtered.append(run(a))
rms=lambda v:math.sqrt(sum(x*x for x in v)/len(v))
assert rms(filtered)<.8*rms(raws)
print('PASS emitted VM: small tremor attenuation, deliberate-turn bypass, menu/tracking/hitch reset, wraparound, 60/72/90/120Hz convergence.')
print('12Hz synthetic yaw RMS ratio:',round(rms(filtered)/rms(raws),3))
