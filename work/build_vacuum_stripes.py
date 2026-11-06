"""Drive the four stripe insets from the stock pawn's vacuum state."""
from pathlib import Path
import struct
from cooked_patch import Package

root = Path(__file__).resolve().parents[2]
work = root / 'work/vacuum-v33'
source = root / 'work/circular-v31/payload/Player/VRGG_Pawn.uasset'
p = Package(source)
level_ref = p.add_property('EkoroVacuumLevel','DeltaTime',p.ref('VRGG_Pawn_C'))
def integer(value):
    return struct.pack('<i', value)

def instance(name):
    return b'\x01' + integer(p.ref(name))

def call(name, args, opcode=b'\x1c'):
    return opcode + integer(p.ref(name)) + args + b'\x16'

def context(obj, expression, result=0):
    return b'\x19' + obj + struct.pack('<Ii', p.size(expression), result) + expression

def valid(obj):
    return call('/Script/Engine.KismetSystemLibrary.IsValid', obj, b'\x68')

def script(pkg):
    body = pkg.body(pkg.index('ReceiveTick'))
    offset = 20 + 4 * struct.unpack_from('<i', body, 16)[0]
    vm, length = struct.unpack_from('<ii', body, offset)
    return body[:offset], vm, body[offset+8:offset+8+length], body[offset+8+length:]

mid = instance('VRGG_Pawn_C.EkoroHeartMID')
pad = instance('VRGG_Pawn_C.PadActor')
flag = '/Game/VRGG/Player/Pad.Pad_C.IsVacuuming'
active = context(pad, instance(flag), p.ref(flag))
level = instance('VRGG_Pawn_C.EkoroVacuumLevel')
def number(value):
    return b'\x1e'+struct.pack('<f',value)
def assign(value):
    return b'\x0f'+integer(level_ref)+level+value
def math_call(name,args):
    return call('/Script/Engine.KismetMathLibrary.'+name,args,b'\x68')
def set_stripes():
    args = b'\x21' + p.name('EkoroVacuumActive') + level
    return context(mid, call('/Script/Engine.MaterialInstanceDynamic.SetScalarParameterValue', args))

prefix = bytearray()
fixups = []
labels = {}
def go(label, predicate=None):
    prefix.append(6 if predicate is None else 7)
    fixups.append((len(prefix),label))
    prefix.extend(bytes(4))
    if predicate is not None:
        prefix.extend(predicate)
go('resume', valid(mid))
go('pink', valid(pad))
go('pink', active)
prefix.extend(assign(number(1)))
go('update')
labels['pink'] = p.size(prefix)
dt=b'\x00'+integer(p.ref('VRGG_Pawn_C.ReceiveTick.DeltaSeconds'))
step=math_call('Divide_FloatFloat',dt+number(.25))
prefix.extend(assign(math_call('FMax',number(0)+math_call('Subtract_FloatFloat',level+step))))
labels['update']=p.size(prefix)
prefix.extend(set_stripes())
labels['resume'] = p.size(prefix)
for pos,label in fixups:
    struct.pack_into('<I', prefix, pos, labels[label])

head, vm, original, tail = script(p)
decoder,_ = p.parse(original)
shifted = bytearray(original)
for pos in decoder.spans:
    if original[pos] in (6,7,76):
        target = struct.unpack_from('<I', original, pos+1)[0]
        struct.pack_into('<I', shifted, pos+1, target+labels['resume'])
code = bytes(prefix)+shifted
p.changes[p.index('ReceiveTick')] = head + struct.pack('<ii',p.size(code),len(code)) + code + tail
path = work/'pawn/VRGG_Pawn'
p.save(path)
# Walk the actual saved prefix for on, release, interruption, and missing objects.
saved=Package(path.with_suffix('.uasset'))
_,_,loaded,_=script(saved)
dec,nodes=saved.parse(loaded)
starts={dec.spans[n[0]][1]:i for i,n in enumerate(nodes)}
assert loaded[len(prefix):]==shifted
for node in nodes:
    if node[1] in ('Jump','JumpIfNot','Push'): assert int(node[2]) in starts
def run(has_mid,has_pad,is_on,level=0,dt=1/90):
    writes=[]
    def ev(n):
        _,op,name,children=n
        nonlocal level
        if op=='Instance': return {'EkoroHeartMID':has_mid,'PadActor':has_pad,'IsVacuuming':is_on,'EkoroVacuumLevel':level}[name.split('.')[-1]]
        if op=='Float':return float(name)
        if op=='Local':assert name.endswith('.DeltaSeconds');return dt
        if op=='Let':level=ev(children[1]);return
        if op=='Context':
            assert ev(children[0])
            return ev(children[-1])
        if op=='Math' and name.endswith('.IsValid'):return ev(children[0])
        if op=='Math':
            a,b=map(ev,children[:2])
            if name.endswith('.FMax'):return max(a,b)
            if name.endswith('.Subtract_FloatFloat'):return a-b
            if name.endswith('.Divide_FloatFloat'):return a/b
        if op=='Call' and name.endswith('.SetScalarParameterValue'):
            assert children[0][2]=='EkoroVacuumActive'
            writes.append(ev(children[1]))
            return
        raise AssertionError((op,name))
    i=0
    while dec.spans[nodes[i][0]][1]<labels['resume']:
        n=nodes[i]
        if n[1]=='Jump' or (n[1]=='JumpIfNot' and not ev(n[3][0])):i=starts[int(n[2])]
        else:
            if n[1]!='JumpIfNot':ev(n)
            i+=1
    return writes
for mid_ok in (False,True):
    for pad_ok in (False,True):
        for on in (False,True):
            assert run(mid_ok,pad_ok,on)==([float(pad_ok and on)] if mid_ok else [])
print('Saved pawn passed all eight state combinations and branch checks.')
for hz in (72,90,120):
    value=1
    for frame in range(1,round(hz*.25)+2):
        value,=run(True,True,False,value,1/hz)
        assert abs(value-max(0,1-frame/(hz*.25)))<.00001
assert run(True,True,True,.4)==[1]
print('Quarter-second release and immediate retrigger verified.')
