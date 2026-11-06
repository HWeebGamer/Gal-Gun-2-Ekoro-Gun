import bpy, math
from pathlib import Path
from mathutils import Vector
root=Path.cwd()
out=root/'outputs/pink-slot-study'
out.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(root/'outputs/white-optic-game/Ekoro_White_Optic_Game.blend'))
scene=bpy.context.scene
cam=bpy.data.objects['Overall']
scene.camera=cam
scene.render.resolution_x=1100
scene.render.resolution_y=780
scene.render.resolution_percentage=100
scene.cycles.samples=24
scene.cycles.use_denoising=True
def render(name):
 scene.render.filepath=str(out/name)
 bpy.ops.render.render(write_still=True)
original_loc=cam.location.copy()
original_scale=cam.data.ortho_scale
cam.location+=cam.rotation_euler.to_quaternion()@Vector((-.020*original_scale,-.055*original_scale*780/1100,0))
cam.data.ortho_scale=.145
render('Slots-before.png')
gun=bpy.data.objects['SK_DevilSweeper_Grip']
tree=gun.data.materials[0].node_tree
shader=next(n for n in tree.nodes if n.type=='BSDF_PRINCIPLED')
atlas=shader.inputs['Base Color'].links[0].from_node
w,h=atlas.image.size
pixels=list(atlas.image.pixels)
def pink(x,y):
 i=4*((h-1-y)*w+x)
 return pixels[i]-pixels[i+1]>.14
xs=[x for x in range(5,67) if pink(x,32)]
runs=[]
for x in xs:
 if runs and x==runs[-1][-1]+1:runs[-1].append(x)
 else:runs.append([x])
assert len(runs)==4,runs
# Generate high-resolution control channels on the same UVs as the painted inserts.
# R encodes the recessed profile; G shades the bevel; B gives the floor a satin finish.
N=1024
import numpy as np
from array import array
data=np.zeros((N,N,4),dtype=np.float32)
data[:,:,0]=1
data[:,:,3]=1
Y,X=np.mgrid[0:N,0:N]
X=(X+.5)*w/N
Y=h-(Y+.5)*h/N
for run in runs:
 cx=(run[0]+run[-1]+1)/2
 ys=[y for y in range(6,59) if pink(int(cx),y)]
 radius=(len(run)/2)
 top,bottom=min(ys),max(ys)+1
 dy=np.maximum(np.maximum(top+radius-Y,Y-(bottom-radius)),0)
 d=radius-np.hypot(X-cx,dy)
 t=np.clip((d+.45)/1.55,0,1)
 t=t*t*(3-2*t)
 data[:,:,0]-=.83*t
 data[:,:,1]=np.maximum(data[:,:,1],(.43*np.exp(-((d-.65)/.68)**2)+.11*t)*np.clip((d+.65)/.65,0,1))
 data[:,:,2]=np.maximum(data[:,:,2],t)
im=bpy.data.images.new('Four pink slots - bevel and inset',width=N,height=N,float_buffer=True)
im.colorspace_settings.name='Non-Color'
im.pixels.foreach_set(data.ravel())
im.pack()
tex=tree.nodes.new('ShaderNodeTexImage');tex.image=im
sep=tree.nodes.new('ShaderNodeSeparateColor')
tree.links.new(tex.outputs['Color'],sep.inputs['Color'])
bump=tree.nodes.new('ShaderNodeBump');bump.label='Rounded lip into inset pink floor'
bump.inputs['Strength'].default_value=.75;bump.inputs['Distance'].default_value=.00085
tree.links.new(sep.outputs[0],bump.inputs['Height']);tree.links.new(bump.outputs[0],shader.inputs['Normal'])
mix=tree.nodes.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY'
tree.links.new(sep.outputs[1],mix.inputs[0]);tree.links.new(atlas.outputs['Color'],mix.inputs[1])
mix.inputs[2].default_value=(.28,.17,.24,1)
tree.links.new(mix.outputs[0],shader.inputs['Base Color'])
rough=tree.nodes.new('ShaderNodeMapRange')
rough.inputs['To Min'].default_value=shader.inputs['Roughness'].default_value
rough.inputs['To Max'].default_value=.40
tree.links.new(sep.outputs[2],rough.inputs['Value']);tree.links.new(rough.outputs[0],shader.inputs['Roughness'])
bpy.ops.wm.save_as_mainfile(filepath=str(out/'Ekoro_Pink_Slots.blend'))
render('Slots-after.png')
cam.location=original_loc
cam.data.ortho_scale=original_scale
render('Overall.png')
