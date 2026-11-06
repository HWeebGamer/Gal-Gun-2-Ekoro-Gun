from pathlib import Path
import bpy, numpy as np, struct
root=Path(__file__).resolve().parents[2]
import sys,bmesh
only_sight='--only-sight' in sys.argv
out=root/('work/circular-v33-only' if only_sight else 'work/circular-v31');out.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(root/'outputs/circular-optic/Ekoro_Circular_Optic.blend'))
def pixels(prefix):
 im=next(i for i in bpy.data.images if i.name.startswith(prefix))
 buf=np.empty(im.size[0]*im.size[1]*4,np.float32);im.pixels.foreach_get(buf)
 return buf.reshape(im.size[1],im.size[0],4)
src=pixels('Ekoro_BaseColor')[:,:,:3]
ctrl=pixels('Heart halves and slots')
edge=pixels('Smooth heart color')
coverage=pixels('Heart edge coverage')[:,:,0:1]
N=ctrl.shape[0]
# Reproduce Blender's linear atlas sampling before blending in the precise edge.
u=(np.arange(N)+.5)*src.shape[1]/N-.5
a=np.floor(u).astype(int);f=(u-a)[None,:,None]
row=src[:,a%src.shape[1]]*(1-f)+src[:,(a+1)%src.shape[1]]*f
rgb=row[a%src.shape[0]]*(1-f.transpose(1,0,2))+row[(a+1)%src.shape[0]]*f.transpose(1,0,2)
rgb=rgb*(1-coverage)+edge[:,:,:3]*coverage
rgb*=1-ctrl[:,:,1:2]*(1-np.array([.28,.17,.24]))
srgb=np.where(rgb<=.0031308,rgb*12.92,1.055*np.maximum(rgb,0)**(1/2.4)-.055)
bgra=np.concatenate([srgb[:,:,::-1],ctrl[:,:,0:1]],axis=2)
(out/'Ekoro_BaseColor.tga').write_bytes(struct.pack('<BBBHHBHHHHBB',0,0,2,0,0,0,0,0,N,N,32,8)+np.uint8(np.clip(bgra,0,1)*255+.5).tobytes())
gun=bpy.data.objects['SK_DevilSweeper_Grip'];rig=next(o for o in bpy.data.objects if o.type=='ARMATURE')
if only_sight:
 bm=bmesh.new()
 bm.from_mesh(gun.data)
 seen=set()
 remove=[]
 for v in bm.verts:
  if v in seen:continue
  component=set()
  pending=[v]
  while pending:
   a=pending.pop()
   if a in component:continue
   component.add(a)
   pending.extend(e.other_vert(a) for e in a.link_edges)
  seen.update(component)
  coords=[gun.matrix_world@a.co for a in component]
  if all(.022<p.y<.072 and -.038<p.z<-.016 and -.014<p.x<.007 for p in coords):
   remove.extend(component)
 assert len(remove)==152,len(remove)
 bmesh.ops.delete(bm,geom=remove,context='VERTS')
 bm.to_mesh(gun.data)
 bm.free()
mat=gun.data.materials[0]
# Flat UV samples avoid sampling the nearby colored insets on the scope.
parts=[bpy.data.objects[n] for n in ('Circular optic','Low adjustment dial')]
for o in parts:
 bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
 for mod in list(o.modifiers):bpy.ops.object.modifier_apply(modifier=mod.name)
 uv=o.data.uv_layers.active or o.data.uv_layers.new()
 for poly in o.data.polygons:
  coloruv=((.619140625,.501953125) if poly.material_index==1 else (.689453125,.115234375))
  for j in poly.loop_indices:uv.data[j].uv=coloruv
 o.data.materials.clear();o.data.materials.append(mat)
 for poly in o.data.polygons:poly.material_index=0
 g=o.vertex_groups.new(name='root');g.add(list(range(len(o.data.vertices))),1,'REPLACE')
bpy.ops.object.select_all(action='DESELECT')
for o in parts+[gun]:o.select_set(True)
bpy.context.view_layer.objects.active=gun;bpy.ops.object.join()
# Keep a single named FBX material; cooked material is authored separately.
mat.node_tree.nodes.clear()
mat.node_tree.nodes.new('ShaderNodeBsdfPrincipled')
rig.select_set(True)
bpy.ops.export_scene.fbx(filepath=str(out/'SK_DevilSweeper_Grip.fbx'),use_selection=True,object_types={'MESH','ARMATURE'},add_leaf_bones=False,bake_anim=False,axis_forward='-Y',axis_up='Z',apply_unit_scale=True,mesh_smooth_type='FACE')
print('Exported',len(gun.data.vertices),'vertices and',N,'pixel color/height atlas')
