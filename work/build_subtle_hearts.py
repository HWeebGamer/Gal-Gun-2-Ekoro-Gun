"""v16: quarter-size hearts with a 40%-strength particle alpha fade."""
import struct,json
from pathlib import Path
from cooked_patch import Package
root=Path(__file__).resolve().parent.parent
p=Package(root/'work/muzzle-pointer-v15/VRGG/Effect/Particles/Shooting/P_EkoroHearts.uasset')
def scale_float_array(raw,factor):
 count=struct.unpack_from('<i',raw)[0]
 assert len(raw)==4+4*count
 values=struct.unpack_from('<'+'f'*count,raw,4)
 return struct.pack('<i',count)+struct.pack('<'+'f'*count,*(v*factor for v in values))
def scale_field(export,field,factor):
 i=p.index(export);body=p.body(i)
 inner=next(body[a:b] for name,kind,extra,start,a,b in p.tags(body) if name==field)
 for name,kind,extra,start,a,b in p.tags(inner):
  if name in ('MinValue','MaxValue','MinValueVec','MaxValueVec'):
   def scaled(raw):
    count=len(raw)//4
    return struct.pack('<'+'f'*count,*(v*factor for v in struct.unpack('<'+'f'*count,raw)))
   body=p.edit(body,[field,name],scaled)
 body=p.edit(body,[field,'Table','Values'],lambda raw:scale_float_array(raw,factor))
 p.changes[i]=body
scale_field('ParticleModuleSize_0','StartSize',.25)
scale_field('ParticleModuleColorOverLife_0','AlphaOverLife',.4)
assert {p.exports[i]['name'] for i in p.changes}=={'ParticleModuleSize_0','ParticleModuleColorOverLife_0'}
dest=root/'work/muzzle-pointer-v16/VRGG/Effect/Particles/Shooting/P_EkoroHearts'
p.save(dest)
# Reopen and verify the exact cooked values, including the zero-alpha endpoint.
q=Package(dest.with_suffix('.uasset'))
def values(export,field):
 body=q.body(q.index(export))
 for key in (field,'Table','Values'):
  body=next(body[a:b] for name,kind,extra,start,a,b in q.tags(body) if name==key)
 count=struct.unpack_from('<i',body)[0];return struct.unpack_from('<'+'f'*count,body,4)
size=values('ParticleModuleSize_0','StartSize');alpha=values('ParticleModuleColorOverLife_0','AlphaOverLife')
assert all(abs(v-.15)<1e-6 for v in size)
assert len(alpha)==2 and abs(alpha[0]-.4)<1e-6 and alpha[1]==0
changed=[e['name'] for i,e in enumerate(p.exports) if p.ns['payload'][e['offset']-p.ns['header_size']:e['offset']-p.ns['header_size']+e['size']]!=q.body(i)]
assert set(changed)=={'ParticleModuleSize_0','ParticleModuleColorOverLife_0'}
report={'size_ratio_to_v15':.25,'particle_alpha_ratio_to_v15':.4,'size_values':size,'alpha_values':alpha,'changed_exports':changed,'burst_count':3,'lifetime_seconds':.38}
(root/'outputs/SubtleHearts_v16_build.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
