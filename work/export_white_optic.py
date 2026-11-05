"""Export approved v2 housing with existing gun skeleton and atlas."""
import bpy,sys
from pathlib import Path
root=Path(__file__).resolve().parents[2]
no_laser='--no-laser' in sys.argv
out=root/('outputs/white-optic-only' if no_laser else 'outputs/white-optic-game');out.mkdir(exist_ok=True)
approved=root/'outputs/white-optic-v2/Ekoro_White_Optic_v2.blend'
if no_laser:
 bpy.ops.wm.open_mainfile(filepath=str(root/'outputs/Ekoro_Gun_Prototype.blend'))
 with bpy.data.libraries.load(str(approved),link=False) as (src,dst):
  dst.collections=['White optic prototype']
 bpy.context.scene.collection.children.link(dst.collections[0])
else:
 bpy.ops.wm.open_mainfile(filepath=str(approved))
gun=bpy.data.objects['SK_DevilSweeper_Grip']
rig=next(o for o in bpy.data.objects if o.type=='ARMATURE')
mat=gun.data.materials[0]
im=next(n.image for n in mat.node_tree.nodes if n.type=='TEX_IMAGE')
pixels=list(im.pixels);w,h=im.size
def sample(target):
 best=None
 for y in range(2,h-2,3):
  for x in range(2,w-2,3):
   rgba=pixels[4*(y*w+x):4*(y*w+x)+4]
   score=sum(abs(rgba[i]-target[i]) for i in range(3))
   if rgba[3]>.9 and (best is None or score<best[0]):best=(score,(x+.5)/w,(y+.5)/h)
 return best[1:]
white=sample((.83,.85,.87));dark=sample((.025,.03,.04))
pieces=list(bpy.data.collections['White optic prototype'].objects)
for o in pieces:
 bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
 for mod in list(o.modifiers):bpy.ops.object.modifier_apply(modifier=mod.name)
 o.data.materials.clear();o.data.materials.append(mat)
 uv=o.data.uv_layers.active or o.data.uv_layers.new()
 for loop in uv.data:loop.uv=dark if o.name=='Optic mounting foot' else white
 group=o.vertex_groups.new(name='root');group.add(list(range(len(o.data.vertices))),1,'REPLACE')
bpy.ops.object.select_all(action='DESELECT');gun.select_set(True)
for o in pieces:o.select_set(True)
bpy.context.view_layer.objects.active=gun;bpy.ops.object.join()
bpy.ops.object.select_all(action='DESELECT');gun.select_set(True);rig.select_set(True)
bpy.ops.export_scene.fbx(filepath=str(out/'SK_DevilSweeper_Grip.fbx'),use_selection=True,object_types={'MESH','ARMATURE'},add_leaf_bones=False,bake_anim=False,axis_forward='-Y',axis_up='Z',apply_unit_scale=True,mesh_smooth_type='FACE',path_mode='COPY',embed_textures=False)
bpy.ops.wm.save_as_mainfile(filepath=str(out/'Ekoro_White_Optic_Game.blend'))
print('OPTIC_EXPORTED',len(gun.data.vertices),white,dark)
