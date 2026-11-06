from pathlib import Path
from math import sin,cos,tau
import bpy,bmesh
from mathutils import Vector
out=Path.cwd()/'outputs/circular-optic'
out.mkdir(exist_ok=True)
heart={}
exec((Path.cwd()/'work/preview_smooth_hearts.py').read_text().split('scene=bpy.context.scene')[0],heart)
# Preserve the border mask explicitly; generated RGB images lose their alpha on packing.
paint=heart['paint']
mask=bpy.data.images.new('Heart edge coverage',width=heart['N'],height=heart['N'],float_buffer=True)
mask.colorspace_settings.name='Non-Color'
coverage=paint.copy()
coverage[:,:,:3]=paint[:,:,3:4]
coverage[:,:,3]=1
mask.pixels.foreach_set(coverage.ravel());mask.update();mask.pack()
node=heart['tree'].nodes.new('ShaderNodeTexImage');node.image=mask
heart['tree'].links.new(node.outputs['Color'],heart['blend'].inputs[0])
bpy.context.preferences.filepaths.save_version=0
gun=bpy.data.objects['SK_DevilSweeper_Grip']
bm=bmesh.new();bm.from_mesh(gun.data)
seen=set();remove=[];old=[]
for v in bm.verts:
 if v in seen:continue
 todo=[v];part=set()
 while todo:
  a=todo.pop()
  if a in part:continue
  part.add(a)
  todo.extend(e.other_vert(a) for e in a.link_edges)
 seen.update(part)
 pts=[gun.matrix_world@a.co for a in part]
 if min(p.z for p in pts)>=.03149 and all(-.135<p.y<-.089 for p in pts):
  remove.extend(part);old.extend(pts)
assert remove
bmesh.ops.delete(bm,geom=remove,context='VERTS');bm.to_mesh(gun.data);bm.free()
width=max(p.x for p in old)-min(p.x for p in old)
assert abs(width-.039)<.0001
cx=-.00358717;cy=-.112;cz=.046
def mat(name,color,metal):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True
 s=m.node_tree.nodes.get('Principled BSDF');s.inputs['Base Color'].default_value=(*color,1);s.inputs['Roughness'].default_value=.32;s.inputs['Metallic'].default_value=metal
 return m
white=mat('Ceramic white housing',(.82,.84,.87),.18);inner=mat('Graphite interior',(.055,.055,.065),.15)
# Axial section in mm, from rear lip to flared objective, returning via the bore.
profile=[(-21,16.4),(-20.4,17),(-17,17),(-16.4,16.3),(-13.5,16.3),(-13,16.9),(-11,16.9),(-10.4,16.3),(0,16.3),(9.5,18.4),(11,18.4),(11.7,19.1),(19.9,19.5),(21,18.7),(21,15.1),(20,14.5),(10,14.4),(-9,13),(-20,13),(-21,13.8)]
verts=[];faces=[];N=96
for y,r in profile:
 for i in range(N):
  ang=tau*i/N
  verts.append((cx+.001*r*cos(ang),cy+.001*y,cz+.001*r*sin(ang)))
for j in range(len(profile)):
 for i in range(N):
  k=(i+1)%N;l=(j+1)%len(profile);faces.append((j*N+i,l*N+i,l*N+k,j*N+k))
mesh=bpy.data.meshes.new('Revolved optic shell');mesh.from_pydata(verts,[],faces);mesh.update()
o=bpy.data.objects.new('Circular optic',mesh);bpy.context.collection.objects.link(o);mesh.materials.append(white);mesh.materials.append(inner)
for p in mesh.polygons:
 section=p.index//N;p.material_index=int(14<=section<=18 or section in (3,));p.use_smooth=section not in (13,19)
# Low adjustment dial.
bpy.ops.mesh.primitive_cylinder_add(vertices=48,radius=.005,depth=.0028,location=(cx,cy-.002,cz+.0168))
cap=bpy.context.object;cap.name='Low adjustment dial';cap.data.materials.append(white)
bev=cap.modifiers.new('Soft edge','BEVEL');bev.width=.00045;bev.segments=3
scene=bpy.context.scene;cam=scene.camera
def view(name,pos,target,scale):
 cam.location=Vector(pos);cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler()
 cam.data.shift_x=0;cam.data.shift_y=0;cam.data.ortho_scale=scale;scene.render.filepath=str(out/(name+'.png'))
view('Overall',(.31,-.31,.17),(0,-.055,-.031),.38)
bpy.ops.wm.save_as_mainfile(filepath=str(out/'Ekoro_Circular_Optic.blend'))
bpy.ops.render.render(write_still=True)
view('Aiming',(cx,cy-.36,cz),(cx,cy,cz),.095)
bpy.ops.render.render(write_still=True)
