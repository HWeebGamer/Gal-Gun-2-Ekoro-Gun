"""Reserve physical right A after the game's optional hand inversion (v19)."""
import json
import struct
from pathlib import Path
from cooked_patch import Package

root = Path(__file__).resolve().parent.parent
source = root.parent / 'UmodelSaved/Game/VRGG/Player/Utils/PlayerInputFunctionLibrary.uasset'
p = Package(source)
reports = {}
for fn in ('CreateActionKeyMapping', 'CreateAxisKeyMapping'):
    index = p.index(fn)
    raw = p.body(index)
    loc = 20 + 4 * struct.unpack_from('<i', raw, 16)[0]
    oldvm, size = struct.unpack_from('<ii', raw, loc)
    old = raw[loc+8:loc+8+size]
    d, nodes = p.parse(old)
    matches = [n for n in nodes if n[1] == 'Let' and n[2].endswith('.CallFunc_Array_Add_ReturnValue')]
    assert len(matches) == 1
    a = matches[0][0]
    b, start, resume = d.spans[a]
    assert old[-1] == 0x53
    key = b'\x2f' + struct.pack('<ii', p.ref('/Script/InputCore.Key'), 32)
    key += b'\x21' + p.name('MotionController_Right_FaceButton1') + b'\x30'
    local = b'\x00' + struct.pack('<i', p.ref('PlayerInputFunctionLibrary_C.' + fn + '.l_Key'))
    equal = b'\x68' + struct.pack('<i', p.ref('/Script/Engine.KismetInputLibrary.EqualEqual_KeyKey')) + local + key + b'\x16'
    # Equal -> skip original Array_Add; unequal -> run it, then return to loop.
    tailvm = oldvm - 1
    addvm = tailvm + 5 + p.size(equal) + 5
    tail = b'\x07' + struct.pack('<I', addvm) + equal
    tail += b'\x06' + struct.pack('<I', resume) + old[a:b]
    tail += b'\x06' + struct.pack('<I', resume) + b'\x53'
    code = old[:a] + b'\x06' + struct.pack('<I', tailvm) + b'\x0b' * (resume-start-5) + old[b:-1] + tail
    nd, nn = p.parse(code)
    vm = p.size(code)
    boundaries = {span[1] for span in nd.spans.values()}
    def check(n):
        if n[1] in ('Jump', 'JumpIfNot', 'Push'):
            assert int(n[2]) in boundaries
        for child in n[3]:
            check(child)
    for n in nn:
        check(n)
    p.changes[index] = raw[:loc] + struct.pack('<ii', vm, len(code)) + code + raw[loc+8+size:]
    reports[fn] = dict(tail_VM=tailvm, add_VM=addvm, resume_VM=resume, old_VM=oldvm, new_VM=vm)

output = root / 'work/muzzle-pointer-v19/VRGG/Player/Utils/PlayerInputFunctionLibrary'
p.save(output)
(root/'outputs/RightA_v19_build.json').write_text(json.dumps(reports, indent=2))
print(json.dumps(reports, indent=2))
