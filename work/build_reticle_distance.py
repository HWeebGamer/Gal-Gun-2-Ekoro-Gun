"""v13: let the VR reticle reach the existing 50 m gameplay trace limit."""
import sys, struct, json, hashlib
from pathlib import Path

root = Path(__file__).resolve().parent.parent
sys.argv = ['reader', str(root/'UmodelSaved/Game/VRGG/Actors/PointerComponent.uasset')]
exec((root/'work/read_pawn_properties.py').read_text().split("print('TABLES'")[0])

default = next(e for e in exports if e['name'] == 'Default__PointerComponent_C')
start = default['offset'] - header_size
body = payload[start:start + default['size']]
def tag(name, value):
    return (struct.pack('<ii', names.index(name), 0)
            + struct.pack('<ii', names.index('FloatProperty'), 0)
            + struct.pack('<iiBf', 4, 0, 0, value))

old = tag('MaxDistance', 500.0)
new = tag('MaxDistance', 5000.0)
assert body.count(old) == 1, 'Unexpected original VR display limit'
assert body.count(tag('MaxTraceDistance', 5000.0)) == 1, 'Unexpected gameplay trace range'
offset = start + body.index(old) + len(old) - 4
patched = payload[:offset] + struct.pack('<f', 5000.0) + payload[offset+4:]
assert len(patched) == len(payload)
assert patched[:offset] == payload[:offset] and patched[offset+4:] == payload[offset+4:]

dest = root/'work/muzzle-pointer-v13/VRGG/Actors/PointerComponent'
dest.parent.mkdir(parents=True, exist_ok=True)
dest.with_suffix('.uasset').write_bytes(data)
dest.with_suffix('.uexp').write_bytes(patched)
report = {'asset':'VRGG/Actors/PointerComponent', 'property':'MaxDistance',
          'old_cm':500, 'new_cm':5000, 'trace_cm_unchanged':5000,
          'scope':'One four-byte default-property value; header and all other payload bytes unchanged',
          'original_uexp_sha256':hashlib.sha256(payload).hexdigest(),
          'patched_uexp_sha256':hashlib.sha256(patched).hexdigest()}
(root/'outputs').mkdir(exist_ok=True)
(root/'outputs/ReticleDistance_v13_build.json').write_text(json.dumps(report, indent=2))
print(json.dumps(report, indent=2))
