"""Author an uncooked UE4.18 material graph, then let UE compile its shaders."""
import struct,uuid,sys
from pathlib import Path
from cooked_patch import Package
root=Path(__file__).resolve().parents[2]
source=Path('G:/GalGun2-ModWork/build-backups/onlysight-v28/DevilSweeper/Ekoro_Prototype_Surface.uasset')
hammer='--hammer' in sys.argv
details='--insets' in sys.argv
vacuum='--vacuum-stripes' in sys.argv
out=root/('work/vacuum-v32/material' if vacuum else 'work/circular-v31/material' if details else 'work/hammer-material' if hammer else 'work/heart-pulse-material');out.mkdir(parents=True,exist_ok=True)
b=source.read_bytes();pos=24+struct.unpack_from('<i',b,20)[0]*20;hs=struct.unpack_from('<i',b,pos)[0]
(out/'input.uasset').write_bytes(b[:hs]);(out/'input.uexp').write_bytes(b[hs:])
p=Package(out/'input.uasset')
def tag(name,kind,value,extra=b''):
 return p.name(name)+p.name(kind)+struct.pack('<ii',len(value),0)+extra+b'\0'+value
def st(name,typ,value):return tag(name,'StructProperty',value,p.name(typ)+bytes(16))
def string(s):return struct.pack('<i',len(s.encode())+1)+s.encode()+b'\0'
def inp(idx):return struct.pack('<8i',idx,0,0,0,0,0,0,0)
def node(cls,name,fields):
 n=p.ns;count=len(p.exports);data=bytearray(n['data']);records=data[n['export_offset']:n['export_offset']+104*count]
 rec=bytearray(records[104:208]);kind=p.add(cls,'Class',p.ref('/Script/Engine'))
 struct.pack_into('<i',rec,0,kind);rec[16:24]=p.name(name)
 struct.pack_into('<qq',rec,28,0,n['header_size']+len(n['payload'])-4)
 struct.pack_into('<5i',rec,84,-1,0,0,0,0)
 offset=len(data);data.extend(records+rec)
 summary=24+struct.unpack_from('<i',data,20)[0]*20;length=struct.unpack_from('<i',data,summary+4)[0];fieldspos=summary+8+abs(length)*(2 if length<0 else 1)+4
 struct.pack_into('<ii',data,fieldspos+16,count+1,offset)
 dep=struct.unpack_from('<i',data,fieldspos+32)[0];end=dep
 for _ in range(count):end+=4+4*struct.unpack_from('<i',data,end)[0]
 newdep=len(data);data.extend(data[dep:end]+struct.pack('<i',0));struct.pack_into('<i',data,fieldspos+32,newdep)
 for j in range(struct.unpack_from('<i',data,fieldspos+68)[0]):struct.pack_into('<i',data,fieldspos+72+j*8,count+1)
 n['data']=bytes(data);n['export_offset']=offset
 e=dict(p.exports[1]);e.update(name=name,**{'class':kind},size=0,offset=n['header_size']+len(n['payload'])-4)
 p.exports.append(e)
 p.changes[count]=fields+st('MaterialExpressionGuid','Guid',uuid.uuid4().bytes)+tag('Material','ObjectProperty',struct.pack('<i',1))+p.name('None')+bytes(4)
 return count+1
uv=node('MaterialExpressionTextureCoordinate','HeartUV',b'')
pulse=node('MaterialExpressionScalarParameter','HeartPulse',tag('ParameterName','NameProperty',p.name('EkoroHeartPulse'))+tag('DefaultValue','FloatProperty',struct.pack('<f',0)))
def custom(name,hlsl,inputs=None):
 inputs=inputs or [('Base',2),('UV',uv),('Pulse',pulse)]
 def connection(label,index):
  if label=='Height':return struct.pack('<8i',index,4,0,1,0,0,0,1)
  return inp(index)
 values=b''.join(tag('InputName','StrProperty',string(n))+st('Input','ExpressionInput',connection(n,i))+p.name('None') for n,i in inputs)
 # UE4 struct array serializes its inner property tag once before the elements.
 inner=p.name('Inputs')+p.name('StructProperty')+struct.pack('<ii',len(values),0)+p.name('CustomInput')+bytes(16)+b'\0'
 fields=tag('Code','StrProperty',string(hlsl))+tag('OutputType','ByteProperty',p.name('CMOT_Float3'),p.name('ECustomMaterialOutputType'))
 fields+=tag('Inputs','ArrayProperty',struct.pack('<i',len(inputs))+inner+values,p.name('StructProperty'))
 return node('MaterialExpressionCustom',name,fields)
mask='float mask=step(0.76,UV.x)*step(UV.x,0.96)*step(0.07,UV.y)*step(UV.y,0.45)*smoothstep(0.12,0.3,Base.r-Base.g); float a=mask*saturate(Pulse); '
inputs=[('Base',2),('UV',uv),('Pulse',pulse)]
base_color='lerp(Base,float3(1.0,0.82,0.90),a*0.85)'
emission='float3(1.0,0.82,0.90)*a*0.22'
if vacuum:
 assert details and hammer
 active=node('MaterialExpressionScalarParameter','VacuumActive',tag('ParameterName','NameProperty',p.name('EkoroVacuumActive')))
 inputs.extend([('Active',active),('Height',2)])
 # Inside this UV island only the four inset slots have reduced height.
 mask+='float stripe=saturate(Active)*step(UV.x,0.265625)*step(UV.y,0.23)*saturate((1-Height)/0.83); '
 base_color=f'lerp({base_color},float3(0,1,1),stripe)'
 emission+='+float3(0,0.1,0.2)*stripe'
base=custom('HeartBasePulse',mask+'return '+base_color+';',inputs)
emissive=custom('HeartEmissionPulse',mask+'return '+emission+';',inputs)
body=p.body(0)
body=p.edit(body,['BaseColor'],lambda old:struct.pack('<i',base)+old[4:])
nodes=[2,uv,pulse,base,emissive]
if vacuum:nodes.append(active)
if details:
 normal=custom('RecessedInsetNormal', '''
float3 dp=GetWorldPosition(Parameters);
float3 tx=Parameters.TangentToWorld[0], ty=Parameters.TangentToWorld[1];
float2 dx=float2(dot(ddx(dp),tx),dot(ddx(dp),ty));
float2 dy=float2(dot(ddy(dp),tx),dot(ddy(dp),ty));
float det=dx.x*dy.y-dx.y*dy.x;
if(abs(det)<0.0000001) return float3(0,0,1);
float2 dh=float2(ddx(Height),ddy(Height))*0.06375;
return normalize(float3((dx.y*dh.y-dy.y*dh.x)/det,(dy.x*dh.x-dx.x*dh.y)/det,1));
''',[('Height',2)])
 rough=custom('InsetSatinFinish','return lerp(0.50,0.40,saturate((1-Height)/0.83));',[('Height',2)])
 nodes.extend([normal,rough])
 body=st('Normal','VectorMaterialInput',inp(normal)+bytes(16))+st('Roughness','ScalarMaterialInput',inp(rough)+bytes(8))+body
if hammer:
 posnode=node('MaterialExpressionPreSkinnedPosition','HammerRestPosition',b'')
 # Five Y/Z positions, mirrored left/right, measured from this grip's cooked vertices (cm).
 pairs=[(17.7744,.8319),(17.0545,.1068),(16.9927,1.7869),(16.7922,-1.3434),(14.5841,1.1271)]
 near=' || '.join(f'all(abs(Pos.yz-float2({y},{z}))<0.01)' for y,z in pairs)
 hlsl=f'if(abs(abs(Pos.x+0.35875)-0.95805)>0.01 || !({near})) return float3(0,0,0); '
 hlsl+='float a=0.13962634*smoothstep(0.25,1.0,Pulse); float2 p=Pos.yz-float2(16.7922,-1.3434); float s=sin(a), c=cos(a); return TransformLocalVectorToWorld(Parameters,float3(0,(c-1)*p.x+s*p.y,-s*p.x+(c-1)*p.y));'
 kick=custom('HammerShotPivot',hlsl,[('Pos',posnode),('Pulse',pulse)])
 nodes.extend([posnode,kick])
 body=st('WorldPositionOffset','VectorMaterialInput',inp(kick)+bytes(16))+body
body=p.edit(body,['Expressions'],lambda _:struct.pack('<i',len(nodes))+struct.pack('<'+'i'*len(nodes),*nodes))
body=p.edit(body,['StateId'],lambda _:uuid.uuid4().bytes)
body=st('EmissiveColor','ColorMaterialInput',inp(emissive)+struct.pack('<I',0)+bytes([128,128,128,255]))+body
p.changes[0]=body
p.save(out/'authored')
(out/'Ekoro_Prototype_Surface.uasset').write_bytes((out/'authored.uasset').read_bytes()+(out/'authored.uexp').read_bytes())
print('Authored masked near-white pink pulse material:',out/'Ekoro_Prototype_Surface.uasset')
