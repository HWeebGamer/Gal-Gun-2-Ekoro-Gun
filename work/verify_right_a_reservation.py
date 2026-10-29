"""Check saved v19 bytecode branches and preservation of other exports."""
import json
import struct
from pathlib import Path
from cooked_patch import Package

root = Path(__file__).resolve().parent.parent
old = Package(root.parent/'UmodelSaved/Game/VRGG/Player/Utils/PlayerInputFunctionLibrary.uasset')
p = Package(root/'work/muzzle-pointer-v19/VRGG/Player/Utils/PlayerInputFunctionLibrary.uasset')
report = json.loads((root/'outputs/RightA_v19_build.json').read_text())
assert old.imports == p.imports
assert len(old.exports) == len(p.exports)
for i, export in enumerate(old.exports):
    if export['name'] not in report:
        assert old.body(i) == p.body(i), export['name']

keys = ['MotionController_Right_FaceButton1', 'MotionController_Right_FaceButton2',
        'MotionController_Left_FaceButton1', 'MotionController_Left_FaceButton2',
        'MotionController_Right_Trigger', 'MotionController_Left_Trigger',
        'Gamepad_FaceButton_Bottom', 'Enter', 'Escape', 'None']
for fn, info in report.items():
    raw = p.body(p.index(fn))
    loc = 20 + 4 * struct.unpack_from('<i', raw, 16)[0]
    vm, size = struct.unpack_from('<ii', raw, loc)
    d, nodes = p.parse(raw[loc+8:loc+8+size])
    assert d.p+d.extra == vm
    starts = {d.spans[n[0]][1]: n for n in nodes}
    def evaluate(n, key):
        _, op, detail, children = n
        if op == 'Local':
            assert detail == 'PlayerInputFunctionLibrary_C.'+fn+'.l_Key'
            return key
        if op == 'Name':
            return detail
        if op == 'Struct':
            assert detail == '/Script/InputCore.Key size=32'
            return evaluate(children[0], key)
        if op == 'Math':
            assert detail == '/Script/Engine.KismetInputLibrary.EqualEqual_KeyKey'
            return evaluate(children[0], key) == evaluate(children[1], key)
        raise AssertionError(n)
    for key in keys:
        pc = info['tail_VM']
        additions = 0
        for _ in range(5):
            if pc == info['resume_VM']:
                break
            n = starts[pc]
            nextpc = d.spans[n[0]][2]
            if n[1] == 'Jump' or (n[1] == 'JumpIfNot' and not evaluate(n[3][0], key)):
                nextpc = int(n[2])
            elif n[1] == 'Let':
                assert pc == info['add_VM']
                assert n[3][1][3][-1][2] == '/Script/Engine.KismetArrayLibrary.Array_Add'
                additions += 1
            pc = nextpc
        assert pc == info['resume_VM']
        assert additions == (key != keys[0]), (fn, key, additions)
print('PASS: 20 emitted mapping paths; all other exports and imports unchanged.')
