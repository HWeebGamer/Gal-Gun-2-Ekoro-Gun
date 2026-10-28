import bpy
import bmesh
import math
import shutil
from pathlib import Path
from mathutils import Vector

workspace = Path(__file__).resolve().parent.parent
staging = Path('G:/GalGun2-ModWork/source')
staging.mkdir(parents=True, exist_ok=True)
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

def import_asset(path):
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=str(path))
    imported = set(bpy.data.objects) - before
    rig = next(obj for obj in imported if obj.type == 'ARMATURE')
    mesh = next(obj for obj in imported if obj.type == 'MESH' and any(mod.type == 'ARMATURE' for mod in obj.modifiers))
    bpy.context.view_layer.update()
    return imported, rig, mesh

source_objects, source_rig, gun = import_asset(workspace / 'work/ekoro-source/weapon_ek_SF/SkeletalMesh3/ek_gun.gltf')
reference_objects, rig, reference = import_asset(workspace / 'work/sweeper-reference/Game/VRGG/Player/DevilSweeper/SK_DevilSweeper.gltf')
source_matrix = gun.matrix_world.copy()
rig_inverse = rig.matrix_world.inverted()
for vertex in gun.data.vertices:
    position = source_matrix @ vertex.co
    vertex.co = rig_inverse @ Vector((position.z, -position.x - 0.14, -position.y - 0.10))
gun.parent = rig
gun.matrix_parent_inverse.identity()
gun.matrix_basis.identity()
gun.modifiers.clear()
modifier = gun.modifiers.new('Original_weapon_skeleton', 'ARMATURE')
modifier.object = rig
gun.vertex_groups.clear()
group = gun.vertex_groups.new(name='root')
group.add(list(range(len(gun.data.vertices))), 1.0, 'REPLACE')
editable = bmesh.new()
editable.from_mesh(gun.data)
bmesh.ops.delete(editable, geom=[face for face in editable.faces if face.material_index != 0], context='FACES')
editable.to_mesh(gun.data)
editable.free()
for obj in list(source_objects | reference_objects):
    if obj not in (gun, rig):
        bpy.data.objects.remove(obj, do_unlink=True)
gun.name = 'SK_DevilSweeper_Grip'
rig.name = 'Armature'
shutil.copy2(workspace / 'work/ekoro-source/weapon_ek_SF/Texture2D/ek_gun_00.png', staging / 'Ekoro_BaseColor.png')
image = bpy.data.images.load(str(staging / 'Ekoro_BaseColor.png'))
material = bpy.data.materials.new('Ekoro_Prototype_Surface')
material.use_nodes = True
shader = material.node_tree.nodes.get('Principled BSDF')
texture = material.node_tree.nodes.new('ShaderNodeTexImage')
texture.image = image
material.node_tree.links.new(texture.outputs['Color'], shader.inputs['Base Color'])
shader.inputs['Roughness'].default_value = 0.7
gun.data.materials.clear()
gun.data.materials.append(material)
bpy.context.scene.unit_settings.system = 'METRIC'
bpy.context.scene['prototype_status'] = 'Revision 3: right-controller grip only, rotated 180 degrees around the grip anchor; stereo/forward shaders cooked separately. Alignment remains provisional.'
bpy.ops.object.select_all(action='DESELECT')
gun.select_set(True)
rig.select_set(True)
bpy.context.view_layer.objects.active = rig
bpy.ops.export_scene.fbx(filepath=str(staging / 'SK_DevilSweeper_Grip.fbx'), use_selection=True, object_types={'MESH', 'ARMATURE'}, add_leaf_bones=False, bake_anim=False, axis_forward='-Y', axis_up='Z', apply_unit_scale=True, mesh_smooth_type='FACE', path_mode='COPY', embed_textures=False)
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=str(workspace / 'outputs/Ekoro_Gun_Prototype.blend'))
bpy.context.view_layer.update()
points = [gun.matrix_world @ vertex.co for vertex in gun.data.vertices]
center = sum(points, Vector()) / len(points)
bpy.ops.object.camera_add(location=center + Vector((0.65, 0.12, 0.1)))
camera = bpy.context.object
camera.rotation_euler = (center-camera.location).to_track_quat('-Z', 'Y').to_euler()
camera.data.type = 'ORTHO'
camera.data.ortho_scale = 0.42
bpy.context.scene.camera = camera
bpy.ops.object.light_add(type='AREA', location=center + Vector((0.4, -0.2, 0.6)))
bpy.context.object.data.energy = 35
bpy.context.object.data.shape = 'DISK'
bpy.context.object.data.size = 0.5
bpy.context.object.rotation_euler = (center-bpy.context.object.location).to_track_quat('-Z', 'Y').to_euler()
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.samples = 16
scene.render.resolution_x = 640
scene.render.resolution_y = 480
scene.render.resolution_percentage = 100
scene.world.color = (0.2, 0.2, 0.2)
scene.render.filepath = str(workspace / 'outputs/Ekoro_Gun_Prototype_Preview.png')
bpy.ops.render.render(write_still=True)
print('PROTOTYPE_READY', len(gun.data.polygons), [bone.name for bone in rig.data.bones])
