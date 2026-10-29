"""v17: keep the approved v16 appearance, but end the burst near the muzzle."""
import struct,json
from pathlib import Path
from cooked_patch import Package
root=Path(__file__).resolve().parent.parent
p=Package(root/'work/muzzle-pointer-v16/VRGG/Effect/Particles/Shooting/P_EkoroHearts.uasset')
i=p.index('ParticleModuleLifetime_0');body=p.body(i)
for field in ('MinValue','MaxValue'):
 def change(raw):
  assert abs(struct.unpack('<f',raw)[0]-.38)<1e-6
  return struct.pack('<f',.08)
 body=p.edit(body,['Lifetime',field],change)
def change_table(raw):
 assert len(raw)==8 and struct.unpack_from('<i',raw)[0]==1
 assert abs(struct.unpack_from('<f',raw,4)[0]-.38)<1e-6
 return struct.pack('<if',1,.08)
body=p.edit(body,['Lifetime','Table','Values'],change_table);p.changes[i]=body
dest=root/'work/muzzle-pointer-v17/VRGG/Effect/Particles/Shooting/P_EkoroHearts'
p.save(dest)
q=Package(dest.with_suffix('.uasset'))
changed=[]
for j,e in enumerate(p.exports):
 start=e['offset']-p.ns['header_size']
 if p.ns['payload'][start:start+e['size']]!=q.body(j):changed.append(e['name'])
assert changed==['ParticleModuleLifetime_0']
assert q.body(i)==body
report={'old_lifetime_seconds':.38,'new_lifetime_seconds':.08,'changed_exports':changed,'size_alpha_velocity_unchanged':True}
(root/'outputs/BriefHearts_v17_build.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
