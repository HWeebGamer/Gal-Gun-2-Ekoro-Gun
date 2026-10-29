"""Blender: append a small under-barrel housing to the confirmed grip mesh."""
import bpy,math,json
from pathlib import Path
from mathutils import Vector
root=Path(__file__).resolve().parent.parent
workspace=root.parent
bpy.ops.wm.open_mainfile(filepath=str(workspace/'outputs/Ekoro_Gun_Prototype.blend'))
gun=bpy.data.objects['SK_DevilSweeper_Grip'];rig=next(o for o in bpy.data.objects if o.type=='ARMATURE')
mat=gun.data.materials[0];image=next(n.image for n in mat.node_tree.nodes if n.type=='TEX_IMAGE')
# Sample dark and pink texels from the existing atlas, retaining its cooked material.
pixels=list(image.pixels);w,h=image.size
def sample(kind):
 best=None
 for y in range(2,h-2,3):
  for x in range(2,w-2,3):
   r,g,b,a=pixels[4*(y*w+x):4*(y*w+x)+4]
   score=(r+g+b) if kind=='dark' else abs(r-.8)+abs(g-.1)+abs(b-.4)
   if a>.9 and (best is None or score<best[0]):best=(score,(x+.5)/w,(y+.5)/h)
 return best[1:]
dark=sample('dark');pink=sample('pink');pieces=[]
def finish(obj,uv):
 obj.data.materials.clear();obj.data.materials.append(mat)
 layer=obj.data.uv_layers.active or obj.data.uv_layers.new()
 for loop in layer.data:loop.uv=uv
 bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 group=obj.vertex_groups.new(name='root');group.add(list(range(len(obj.data.vertices))),1,'REPLACE');pieces.append(obj)
def box(name,location,dimensions,uv):
 bpy.ops.mesh.primitive_cube_add(size=1,location=location);obj=bpy.context.object;obj.name=name;obj.dimensions=dimensions
 finish(obj,uv)
 bevel=obj.modifiers.new('Soft edges','BEVEL');bevel.width=.001;bevel.segments=2;bpy.ops.object.modifier_apply(modifier=bevel.name)
x=-.00358717
box('Laser housing',(x,.047,-.030),(.018,.044,.014),dark)
box('Laser mounting rail',(x,.041,-.020),(.012,.028,.007),dark)
bpy.ops.mesh.primitive_cylinder_add(vertices=20,radius=.0045,depth=.002,location=(x,.0695,-.030),rotation=(math.pi/2,0,0))
finish(bpy.context.object,pink)
bpy.ops.object.select_all(action='DESELECT');gun.select_set(True)
for obj in pieces:obj.select_set(True)
bpy.context.view_layer.objects.active=gun;bpy.ops.object.join()
bpy.ops.object.select_all(action='DESELECT');gun.select_set(True);rig.select_set(True);bpy.context.view_layer.objects.active=gun
out=root/'outputs';out.mkdir(exist_ok=True)
bpy.ops.export_scene.fbx(filepath=str(out/'SK_DevilSweeper_Grip_Laser.fbx'),use_selection=True,object_types={'MESH','ARMATURE'},add_leaf_bones=False,bake_anim=False,axis_forward='-Y',axis_up='Z',apply_unit_scale=True,mesh_smooth_type='FACE',path_mode='COPY',embed_textures=False)
bpy.ops.wm.save_as_mainfile(filepath=str(out/'Ekoro_Gun_Laser.blend'))
# Static orthographic preview for placement inspection.
center=Vector((x,.02,-.025))
bpy.ops.object.camera_add(location=center+Vector((.45,.3,.15)));camera=bpy.context.object;camera.rotation_euler=(center-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.type='ORTHO';camera.data.ortho_scale=.32
scene=bpy.context.scene;scene.camera=camera;scene.render.engine='CYCLES';scene.cycles.samples=16;scene.render.resolution_x=900;scene.render.resolution_y=650;scene.render.resolution_percentage=100
bpy.ops.object.light_add(type='AREA',location=center+Vector((.3,.1,.4)));bpy.context.object.data.energy=30
scene.render.filepath=str(out/'Ekoro_Laser_Preview.png');bpy.ops.render.render(write_still=True)
print('LASER_ATTACHMENT_READY',dark,pink)
