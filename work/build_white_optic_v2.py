import bpy,math
from pathlib import Path
from mathutils import Vector
root=Path(__file__).resolve().parents[2];out=root/'outputs/white-optic-v2';out.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(root/'repo/outputs/Ekoro_Gun_Laser.blend'))
for o in list(bpy.data.objects):
 if o.type in ('LIGHT','CAMERA'):bpy.data.objects.remove(o,do_unlink=True)
def material(name,color,metal=0):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Roughness'].default_value=.32;p.inputs['Metallic'].default_value=metal;return m
white=material('Optic - warm white',(.83,.85,.87),.25);dark=material('Optic - inner rim',(.025,.03,.04))
x=-.00358717;y=-.112
col=bpy.data.collections.new('White optic prototype');bpy.context.scene.collection.children.link(col)
def box(name,loc,size,mat):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.dimensions=size;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(mat)
 for c in list(o.users_collection):c.objects.unlink(o)
 col.objects.link(o);b=o.modifiers.new('Rounded edges','BEVEL');b.width=.0015;b.segments=3;return o
box('Optic mounting foot',(x,y,.024),(.027,.039,.008),dark)
box('White sight base',(x,y,.030),(.036,.042,.007),white)
for sign in [-1,1]:box('Sight frame side',(x+sign*.017,y,.046),(.005,.014,.029),white)
box('Sight frame top',(x,y,.060),(.037,.014,.005),white)
# Clear opening: reticle will be a view-dependent game effect, not a solid bead.
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=24;scene.render.resolution_x=1200;scene.render.resolution_y=900;scene.render.resolution_percentage=100
scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.035,.045,.07,1)
for loc,power in [((.3,.15,.4),22),((-.3,-.3,.25),16)]:
 bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.data.energy=power;o.data.size=.35;o.rotation_euler=(Vector((0,-.06,0))-o.location).to_track_quat('-Z','Y').to_euler()
def cam(name,loc,target,scale):
 bpy.ops.object.camera_add(location=loc);o=bpy.context.object;o.name=name;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();o.data.type='ORTHO';o.data.ortho_scale=scale;return o
cameras=[cam('Overall',(.36,.25,.22),(0,-.06,-.025),.36),cam('Rear optic',(.06,-.45,.12),(x,y,.03),.19)]
scene.camera=cameras[0]
for im in bpy.data.images:
 if im.source=='FILE' and not im.packed_file:
  try:im.pack()
  except RuntimeError:pass
bpy.ops.wm.save_as_mainfile(filepath=str(out/'Ekoro_White_Optic_v2.blend'))
for i,c in enumerate(cameras):scene.camera=c;scene.render.filepath=str(out/('Overall.png' if i==0 else 'Rear.png'));bpy.ops.render.render(write_still=True)
(out/'README.txt').write_text('White optic housing prototype. Mounted on original gun/laser reference, no hand or inertia. Centre X=-0.00358717m, axis +Y parallel to barrel; sight centre Z about .046m. Functional white reticle needs projection of current crosshair ray through optic plane, visibility clipped to aperture, per-eye VR verification. Do not use fixed glass-centre dot as proof of crosshair alignment. Assets are design only, not cooked/installed.\n')
