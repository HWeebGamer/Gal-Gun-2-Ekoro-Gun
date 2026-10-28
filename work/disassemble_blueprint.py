"""Read-only UE 4.18 cooked Blueprint bytecode inspection."""
import sys, struct
from pathlib import Path
exec((Path(__file__).parent/'read_pawn_properties.py').read_text().split("print('TABLES'")[0])
opnames = {0:'Local',1:'Instance',2:'Default',4:'Return',6:'Jump',7:'JumpIfNot',11:'Nothing',15:'Let',20:'LetBool',22:'EndParams',23:'Self',25:'Context',26:'ContextSilent',27:'Virtual',28:'Call',29:'Int',30:'Float',32:'Object',33:'Name',34:'Rotation',35:'Vector',36:'Byte',37:'Zero',38:'One',39:'True',40:'False',42:'Null',46:'Cast',47:'Struct',48:'EndStruct',56:'PrimitiveCast',66:'Member',72:'Out',76:'Push',77:'Pop',78:'ComputedJump',79:'PopIfNot',83:'EndScript',95:'LetObj',100:'LetPersistent',104:'Math',105:'Switch'}
class Decoder:
 def __init__(self,b): self.b=b; self.p=0; self.extra=0; self.spans={}
 def read(self,fmt):
  v=struct.unpack_from('<'+fmt,self.b,self.p); self.p+=struct.calcsize('<'+fmt); return v[0] if len(v)==1 else v
 def expr(self,depth=0):
  start=self.p; memstart=start+self.extra; op=self.read('B'); detail=''; children=[]
  def ref():
   self.extra+=4
   return reference(self.read('i'))
  def child(): children.append(self.expr(depth+1))
  def until(end):
   while self.b[self.p]!=end: child()
   child()
  if op in (0,1,2,32,72): detail=ref()
  elif op in (6,76,91): detail=str(self.read('I'))
  elif op in (7,24): detail=str(self.read('I')); child()
  elif op in (4,78,79,81,93,103): child()
  elif op in (15,): detail=ref(); child(); child()
  elif op in (20,67,68,92,95,96,98,107): child(); child()
  elif op in (19,46,66,82,84,85,100): detail=ref(); child()
  elif op in (18,25,26): child(); detail=f'skip={self.read("I")} result={ref()}'; child()
  elif op in (28,99,104): detail=ref(); until(22)
  elif op==27: detail=fname(self.b,self.p); self.p+=8; self.extra+=4; until(22)
  elif op in (33,75): detail=fname(self.b,self.p); self.p+=8; self.extra+=4
  elif op==97: detail=fname(self.b,self.p); self.p+=8; self.extra+=4; child(); child()
  elif op==29: detail=str(self.read('i'))
  elif op==30: detail=str(self.read('f'))
  elif op in (34,35): detail=str(self.read('3f'))
  elif op==43: detail=str(self.read('10f'))
  elif op in (36,44): detail=str(self.read('B'))
  elif op==56: detail=str(self.read('B')); child()
  elif op==47: detail=f'{ref()} size={self.read("i")}'; until(48)
  elif op==49: child(); until(50)
  elif op in (101,61): detail=f'{ref()} count={self.read("i")}'; until(102 if op==101 else 62)
  elif op==105:
   n=self.read('H'); detail=f'cases={n} end={self.read("I")}'; child()
   for i in range(n): child(); detail+=f' next={self.read("I")}'; child()
   child()
  elif op in (31,52):
   unit=2 if op==52 else 1; s=self.p
   while any(self.b[self.p:self.p+unit]): self.p+=unit
   detail=repr(self.b[s:self.p]); self.p+=unit
  elif op not in (11,21,22,23,37,38,39,40,42,45,48,50,58,60,62,64,66,77,80,83,90,94,102):
   raise ValueError(f'Unknown opcode {op:02x} at {start:x}')
  self.spans[start]=(self.p,memstart,self.p+self.extra)
  return (start,opnames.get(op,hex(op)),detail,children)
def render(node,depth=0):
 start,op,detail,children=node
 print('  '*depth+f'{start:04x} {op} {detail}')
 for c in children: render(c,depth+1)
for e in exports:
 if reference(e['class']).endswith('.Function') and (len(sys.argv)<3 or e['name'] in sys.argv[2:]):
  b=payload[e['offset']-header_size:e['offset']-header_size+e['size']]
  n=struct.unpack_from('<i',b,16)[0]; loc=20+4*n
  memory_size,storage_size=struct.unpack_from('<ii',b,loc)
  print('\nFUNCTION',e['name'],'scriptOffset',loc+8,'memory',memory_size,'storage',storage_size)
  d=Decoder(b[loc+8:loc+8+storage_size])
  try:
   while d.p<len(d.b): render(d.expr())
   assert d.p+d.extra==memory_size, (d.p+d.extra,memory_size)
  except (ValueError,IndexError,struct.error) as ex: print('ERROR',ex)
