"""Check pulse VM changes, original behavior preservation and shader isolation."""
import json,struct,math
from pathlib import Path
from cooked_patch import Package
root=Path(__file__).resolve().parents[1]
old=Package(root/'work/muzzle-pointer-v28/VRGG/Player/VRGG_Pawn.uasset')
new=Package(root/'work/muzzle-pointer-v29/VRGG/Player/VRGG_Pawn.uasset')
report=json.loads((root/'outputs/HeartPulse_v29_build.json').read_text())
def script(p,name):
 b=p.body(p.index(name));o=20+4*struct.unpack_from('<i',b,16)[0];_,s=struct.unpack_from('<ii',b,o)
 return b[o+8:o+8+s]
for i,e in enumerate(old.exports):
 if e['name'] not in ('VRGG_Pawn_C','ReceiveTick','Shot'):assert old.body(i)==new.body(i),e['name']
tick=script(new,'ReceiveTick');d,nodes=new.parse(tick);limit=report['tick_prefix_vm']
start=next(n[0] for n in nodes if d.spans[n[0]][1]==limit)
rest=bytearray(tick[start:]);rd,_=new.parse(rest)
for a in rd.spans:
 if rest[a] in (6,7,76):struct.pack_into('<I',rest,a+1,struct.unpack_from('<I',rest,a+1)[0]-limit)
assert bytes(rest)==script(old,'ReceiveTick'),'Original stabilization tick changed'
prefix=[n for n in nodes if d.spans[n[0]][1]<limit]
fade=next(n for n in prefix if n[1]=='Let')
def ev(n,value,dt):
 _,op,name,ch=n
 if op=='Float':return float(name)
 if op=='Local':assert name.endswith('.DeltaSeconds');return dt
 if op=='Instance':assert name.endswith('.EkoroHeartPulse');return value
 if op=='Math':
  args=[ev(c,value,dt) for c in ch if c[1]!='EndParams']
  fn=name.split('.')[-1]
  if fn=='FMax':return max(args)
  if fn=='Subtract_FloatFloat':return args[0]-args[1]
  if fn=='Divide_FloatFloat':return args[0]/args[1]
 raise AssertionError((op,name))
for hz in (60,72,90,120):
 value=1
 for _ in range(math.ceil(.16*hz)+1):value=ev(fade[3][1],value,1/hz)
 assert value==0
assert ev(fade[3][1],0,1/90)==0
assert 0<ev(fade[3][1],1,1/90)<1
assert ev(fade[3][1],1,1)==0
def spawn(n):return (n[1]=='Call' and n[2].endswith('.SpawnEmitterAtLocation')) or any(spawn(c) for c in n[3])
a=script(old,'Shot');ad,an=old.parse(a);b=script(new,'Shot')
n=next(n for n in an if n[1]=='Context' and spawn(n));end,ms,me=ad.spans[n[0]]
assert a[:n[0]]==b[:n[0]],'Shot guards changed'
replacement_end=n[0]+5+(me-ms-5)
assert b[replacement_end:replacement_end+len(a[end:-1])]==a[end:-1]
print('PASS: original tick restored byte-for-byte after relocation; shot guards and all unrelated exports unchanged; emitted fade settles at 60/72/90/120Hz.')
