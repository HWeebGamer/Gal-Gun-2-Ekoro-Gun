"""Small UE4.18 cooked-package editor preserving existing object indices."""
import struct, sys, zlib
from pathlib import Path
def hashes(s):
 h=0
 for ch in s.upper().encode('ascii'):
  v=((h^ch)&255)<<24
  for _ in range(8):v=((v<<1)^(0x04c11db7 if v&0x80000000 else 0))&0xffffffff
  h=(h>>8)^v
 return h&65535,zlib.crc32(s.encode('utf-32-le'))&65535
class Package:
 def __init__(self,path):
  sys.argv=['decoder',str(path)];ns={'__file__':str(Path(__file__).parent/'disassemble_blueprint.py')}
  exec((Path(__file__).parent/'disassemble_blueprint.py').read_text().split('for e in exports:')[0],ns)
  self.ns=ns;self.names=ns['names'];self.imports=ns['imports'];self.exports=ns['exports'];self.original_names=len(self.names);self.original_imports=len(self.imports);self.added=bytearray();self.changes={}
 def ref(self,s):
  hits=[i for i in range(-len(self.imports),len(self.exports)+1) if self.ns['reference'](i)==s]
  assert len(hits)==1,s
  return hits[0]
 def name(self,s):
  if s not in self.names:self.names.append(s)
  return struct.pack('<ii',self.names.index(s),0)
 def add(self,s,kind,outer=0,package='/Script/CoreUObject'):
  full=self.ns['reference'](outer)+'.'+s if outer else s
  for i in range(-len(self.imports),0):
   if self.ns['reference'](i)==full:return i
  self.added.extend(self.name(package)+self.name(kind)+struct.pack('<i',outer)+self.name(s));self.imports.append((s,outer));return -len(self.imports)
 def index(self,name):return next(i for i,e in enumerate(self.exports) if e['name']==name)
 def body(self,i):
  e=self.exports[i];p=e['offset']-self.ns['header_size'];return self.changes.get(i,self.ns['payload'][p:p+e['size']])
 def parse(self,code):
  d=self.ns['Decoder'](code);nodes=[]
  while d.p<len(code):nodes.append(d.expr())
  return d,nodes
 def size(self,code):
  d,_=self.parse(code);return d.p+d.extra
 def save(self,path):
  n=self.ns;header=bytearray(n['data']);no=len(header)
  for s in self.names:
   b=s.encode()+b'\0';header.extend(struct.pack('<i',len(b))+b+struct.pack('<HH',*hashes(s)))
  io=len(header);header.extend(n['data'][n['import_offset']:n['import_offset']+28*self.original_imports]+self.added);hs=len(header)
  summary=24+n['integer'](20)*20;_,end=n['string'](summary+4);fields=end+4
  struct.pack_into('<i',header,summary,hs);struct.pack_into('<ii',header,fields,len(self.names),no);struct.pack_into('<ii',header,fields+24,len(self.imports),io)
  for i in range(n['integer'](fields+68)):struct.pack_into('<i',header,fields+76+8*i,len(self.names))
  result=bytearray();cursor=0
  for i,e in sorted(enumerate(self.exports),key=lambda x:x[1]['offset']):
   start=e['offset']-n['header_size'];result.extend(n['payload'][cursor:start]);offset=hs+len(result);body=self.body(i);result.extend(body)
   struct.pack_into('<qq',header,n['export_offset']+104*i+28,len(body),offset);cursor=start+e['size']
  result.extend(n['payload'][cursor:]);needle=struct.pack('<q',n['header_size']+len(n['payload'])-4)
  hits=[i for i in range(n['name_offset']-7) if header[i:i+8]==needle];assert len(hits)==1
  struct.pack_into('<q',header,hits[0],hs+len(result)-4)
  path=Path(path);path.parent.mkdir(parents=True,exist_ok=True);path.with_suffix('.uasset').write_bytes(header);path.with_suffix('.uexp').write_bytes(result)
 def tags(self,buf):
  p=0
  while True:
   start=p;name=self.ns['fname'](buf,p);p+=8
   if name=='None':return
   kind=self.ns['fname'](buf,p);length=struct.unpack_from('<i',buf,p+8)[0];p+=16;extra=''
   if kind=='StructProperty':extra=self.ns['fname'](buf,p);p+=24
   elif kind=='BoolProperty':p+=1
   elif kind in ('ArrayProperty','ByteProperty','EnumProperty'):extra=self.ns['fname'](buf,p);p+=8
   guid=buf[p];p+=1+16*guid
   yield name,kind,extra,start,p,p+length
   p+=length
 def edit(self,buf,path,fn):
  name,*rest=path
  tag=next(t for t in self.tags(buf) if t[0]==name);_,kind,extra,start,a,b=tag
  value=self.edit(buf[a:b],rest,fn) if rest else fn(buf[a:b])
  header=bytearray(buf[start:a]);struct.pack_into('<i',header,16,len(value))
  return buf[:start]+header+value+buf[b:]
