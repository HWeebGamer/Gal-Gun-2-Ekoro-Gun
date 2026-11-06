from pathlib import Path
import bpy
import numpy as np
from mathutils import Vector

root=Path.cwd()/'outputs'
out=root/'pink-heart-smooth'
out.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(root/'pink-slot-study/Ekoro_Pink_Slots.blend'))
gun=bpy.data.objects['SK_DevilSweeper_Grip']
tree=gun.data.materials[0].node_tree
control=next(n for n in tree.nodes if n.type=='TEX_IMAGE' and n.image.name.startswith('Four pink slots'))
atlas=next(n.image for n in tree.nodes if n.type=='TEX_IMAGE' and n!=control)
w,h=atlas.size
atlas_rgb=np.array(atlas.pixels[:]).reshape(h,w,4)[::-1]
contrast=atlas_rgb[:,:,0]-atlas_rgb[:,:,1]
# Trace the shared half-heart UV island to sub-texel precision.
left=[];right=[]
for y in range(18,116):
 row=contrast[y]
 xs=np.where(row[192:248]>.22)[0]+192
 if len(xs)==0:continue
 a,b=xs[0],xs[-1]
 left.append((a-.5+(.22-row[a-1])/(row[a]-row[a-1]),y+.5))
 right.append((b+.5+(row[b]-.22)/(row[b]-row[b+1]),y+.5))
outline=np.array(left+right[::-1])
assert len(left)>65 and outline[:,0].min()>193
# Smooth over several source texels along the perimeter. Equal arc-length
# spacing keeps steep edges as smooth as the nearly vertical center seam.
closed=np.vstack([outline,outline[0]])
arc=np.r_[0,np.cumsum(np.linalg.norm(np.diff(closed,axis=0),axis=1))]
samples=np.arange(0,arc[-1],.4)
curve=np.column_stack([np.interp(samples,arc,closed[:,axis]) for axis in (0,1)])
steps=np.arange(-18,19)
weights=np.exp(-.5*(steps/5.5)**2)
outline=sum(weight*np.roll(curve,int(step),axis=0) for step,weight in zip(steps,weights))/weights.sum()
N=control.image.size[0]
data=np.array(control.image.pixels[:],dtype=np.float32).reshape(N,N,4)
cols=np.arange(int(191*N/w),int(249*N/w));rows=np.arange(int((h-118)*N/h),int((h-17)*N/h))
X,Y=np.meshgrid((cols+.5)*w/N,h-(rows+.5)*h/N)
inside=np.zeros(X.shape,dtype=bool)
dist=np.full(X.shape,np.inf)
for (ax,ay),(bx,by) in zip(outline,np.roll(outline,-1,axis=0)):
 dx,dy=bx-ax,by-ay
 if dx*dx+dy*dy<1e-12:continue
 t=np.clip(((X-ax)*dx+(Y-ay)*dy)/(dx*dx+dy*dy),0,1)
 dist=np.minimum(dist,np.hypot(X-ax-t*dx,Y-ay-t*dy))
 if abs(dy)>1e-10:inside^=((ay>Y)!=(by>Y))&(X<ax+(Y-ay)*dx/dy)
d=np.where(inside,dist,-dist)
t=np.clip((d+.45)/1.55,0,1);t=t*t*(3-2*t)
region=data[rows[0]:rows[-1]+1,cols[0]:cols[-1]+1]
region[:,:,0]=1-.83*t
region[:,:,1]=(.43*np.exp(-((d-.65)/.68)**2)+.11*t)*np.clip((d+.65)/.65,0,1)
region[:,:,2]=t
im=bpy.data.images.new('Heart halves and slots - recessed profile',width=N,height=N,float_buffer=True)
im.colorspace_settings.name='Non-Color'
im.pixels.foreach_set(data.ravel());im.update();im.pack()
control.image=im
# Replace just the narrow painted border using the same signed distance as
# the bump. Sample either side locally to preserve the atlas color gradients.
gy,gx=np.gradient(d)
length=np.maximum(np.hypot(gx,gy),1e-6)
nx,ny=gx/length,-gy/length
def nearby(offset):
 return atlas_rgb[np.clip((Y+ny*offset).astype(int),0,h-1),np.clip((X+nx*offset).astype(int),0,w-1),:3]
coverage=np.clip((d+.25)/.72,0,1)
coverage=coverage**2*(3-2*coverage)
paint=np.zeros_like(data)
band=paint[rows[0]:rows[-1]+1,cols[0]:cols[-1]+1]
band[:,:,:3]=nearby(-4-d)*(1-coverage[:,:,None])+nearby(4-d)*coverage[:,:,None]
band[:,:,3]=np.clip(4.5-np.abs(d),0,1)
border=bpy.data.images.new('Smooth heart color edge',width=N,height=N,float_buffer=True)
border.colorspace_settings.name='Non-Color'
border.alpha_mode='CHANNEL_PACKED'
border.pixels.foreach_set(paint.ravel());border.update();border.pack()
tex=tree.nodes.new('ShaderNodeTexImage');tex.image=border
shade=next(n for n in tree.nodes if n.type=='MIX_RGB' and n.blend_type=='MULTIPLY')
original=shade.inputs[1].links[0].from_socket
blend=tree.nodes.new('ShaderNodeMixRGB')
tree.links.new(original,blend.inputs[1]);tree.links.new(tex.outputs['Color'],blend.inputs[2])
tree.links.new(tex.outputs['Alpha'],blend.inputs[0]);tree.links.new(blend.outputs[0],shade.inputs[1])
scene=bpy.context.scene
cam=scene.camera
target=Vector((-.00359,-.109,-.024))
for side,name in [(1,'Right'),(-1,'Left')]:
 cam.location=target+Vector((side*.4,.10,.085))
 cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
 cam.data.ortho_scale=.155
 if side==1:bpy.ops.wm.save_as_mainfile(filepath=str(out/'Ekoro_Recessed_Hearts.blend'))
 scene.render.filepath=str(out/(name+'.png'))
 bpy.ops.render.render(write_still=True)
