import struct
import sys
from pathlib import Path

path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parent.parent / 'UmodelSaved/Game/VRGG/Player/VRGG_Pawn.uasset'
data = path.read_bytes()
payload = path.with_suffix('.uexp').read_bytes()
def integer(offset):
    return struct.unpack_from('<i', data, offset)[0]
def string(offset):
    length = integer(offset)
    count = abs(length) * (2 if length < 0 else 1)
    return data[offset+4:offset+4+count].decode('utf-16-le' if length < 0 else 'utf-8').rstrip('\0'), offset+4+count
offset = 24 + integer(20)*20
header_size = integer(offset)
folder, offset = string(offset+4)
flags = integer(offset)
name_count, name_offset, text_count, text_offset, export_count, export_offset, import_count, import_offset = struct.unpack_from('<8i', data, offset+4)
names = []
offset = name_offset
for index in range(name_count):
    value, offset = string(offset)
    names.append(value)
    offset += 4
def fname(buffer, offset):
    index, number = struct.unpack_from('<2i', buffer, offset)
    return names[index] + (f'_{number-1}' if number else '')
imports = []
for index in range(import_count):
    offset = import_offset + index*28
    imports.append((fname(data, offset+20), integer(offset+16)))
exports = []
for index in range(export_count):
    offset = export_offset + index*104
    exports.append({'name': fname(data, offset+16), 'class': integer(offset), 'outer': integer(offset+12), 'size': struct.unpack_from('<q', data, offset+28)[0], 'offset': struct.unpack_from('<q', data, offset+36)[0]})
def reference(index, depth=0):
    if index == 0 or depth > 12:
        return 'None'
    if index < 0:
        name, outer = imports[-index-1]
    else:
        export = exports[index-1]
        name, outer = export['name'], export['outer']
    return (reference(outer, depth+1)+'.' if outer else '')+name
def properties(export):
    buffer = payload[export['offset']-header_size:export['offset']-header_size+export['size']]
    cursor = 0
    while cursor+8 <= len(buffer):
        name = fname(buffer, cursor)
        cursor += 8
        if name == 'None':
            break
        kind = fname(buffer, cursor)
        size, array_index = struct.unpack_from('<2i', buffer, cursor+8)
        cursor += 16
        extra = ''
        if kind == 'StructProperty':
            extra = fname(buffer, cursor)
            cursor += 24
        elif kind == 'BoolProperty':
            extra = bool(buffer[cursor])
            cursor += 1
        elif kind in ('ByteProperty', 'EnumProperty', 'ArrayProperty'):
            extra = fname(buffer, cursor)
            cursor += 8
        elif kind in ('MapProperty', 'SetProperty'):
            cursor += 16 if kind == 'MapProperty' else 8
        has_guid = buffer[cursor]
        cursor += 1 + (16 if has_guid else 0)
        raw = buffer[cursor:cursor+size]
        if kind in ('ObjectProperty', 'ClassProperty'):
            value = reference(struct.unpack('<i', raw)[0])
        elif kind == 'NameProperty' or (kind in ('EnumProperty', 'ByteProperty') and size == 8):
            value = fname(raw, 0)
        elif kind == 'StructProperty' and extra in ('Vector', 'Rotator'):
            value = struct.unpack('<3f', raw)
        elif kind == 'ArrayProperty' and extra == 'ObjectProperty':
            count = struct.unpack_from('<i', raw)[0]
            value = [reference(struct.unpack_from('<i', raw, 4+index*4)[0]) for index in range(count)]
        else:
            value = raw.hex() if size < 80 else f'{size} bytes'
        print(' ', name, kind, extra, value)
        cursor += size

print('TABLES', name_count, export_count, import_count, 'header', header_size)
for export in exports:
    class_name = reference(export['class'])
    targets = sys.argv[2:] if len(sys.argv) > 2 else ('ControllerR_GEN_VARIABLE','PoseMesh_GEN_VARIABLE','MotionControllerL_GEN_VARIABLE','MotionControllerR_GEN_VARIABLE','ControllerRScene_GEN_VARIABLE')
    if export['name'] in targets or (len(sys.argv) < 3 and class_name.endswith('.SCS_Node')):
        print('\nOBJECT', export['name'], class_name)
        try:
            properties(export)
        except (IndexError, struct.error, UnicodeError) as error:
            print('UNPARSED', error)
