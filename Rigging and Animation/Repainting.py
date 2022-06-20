import bpy
import bmesh

bpy.ops.object.mode_set(mode='EDIT')

obj = bpy.context.view_layer.objects.active
me = obj.data
bm = bmesh.from_edit_mesh(me)

vertex_indices_with_adjvert = {}
for v in bm.verts:
    vert_and_links = []
    for e in v.link_edges:
        vert_and_links.append(e.other_vert(v).index)
    
    vertex_indices_with_adjvert[v.index] = vert_and_links
    
######
bpy.ops.object.mode_set(mode='OBJECT')

if not me.vertex_colors:
    me.vertex_colors.new()
    
color_layer = me.vertex_colors.active 

i = 0
for poly in me.polygons:
    for idx in poly.loop_indices:
        loop = me.loops[idx]
        v = loop.vertex_index
        
        color = [0.0, 0.0, 0.0]
        count = 0
        if color_layer.data[i].color[3] == 0:
            for av in vertex_indices_with_adjvert[v]:
                av_color = color_layer.data[av].color
                if color_layer.data[av].color[3] != 0:
                    count = count + 1
                    color[0] = color[0] + av_color[0]
                    color[1] = color[1] + av_color[1]
                    color[2] = color[2] + av_color[2]
            
            if count != 0:
                color_layer.data[i].color = (color[0] / count, color[1] / count, color[2] / count, 1.0)
                
        i += 1