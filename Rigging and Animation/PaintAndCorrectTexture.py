import bpy
import math
import json
import pathlib
import numpy as np

class cf(): # common functions
    
    MAIN_DIR = str(pathlib.Path(__file__).parent.parent.resolve())
    JOINTS_MAP = ['Nose', 'Neck', 'RShoulder', 'RElbow' ,'RWrist', 'LShoulder',
               'LElbow', 'LWrist', 'MidHip', 'RHip', 'RKnee', 'RAnkle', 'LHip',
               'LKnee', 'LAnkle', 'REye', 'LEye', 'REar', 'LEar', 'LBigToe',
               'LSmallToe', 'LHeel', 'RBigToe', 'RSmallToe', 'RHeel']
    
    @staticmethod
    def parse_pose_25(Dir):
        f = open(Dir)
        data = json.load(f)
        arr = data['people'][0]['pose_keypoints_2d']

        Dict = {}
        for i in range(25):
            j=i*3
            Dict[cf.JOINTS_MAP[i]] = [arr[j], 1-arr[j+1], arr[j+2]]

        return Dict

    @staticmethod
    def getAngle_2pts(p1, p2, degree=False):
        dx = p2[0] - p1[0]
        dy = p2[1] - p1[1]
        angle = math.atan2(dy, dx)

        if degree:
            angle = math.degrees(angle)
            
        return angle
    
    
def readRigInfo(fileName):
    with open(fileName, "r") as read_file:
        rigInfo = json.load(read_file)
    
    return rigInfo

def parse_face_80(Dir):
    f = open(Dir)
    data = json.load(f)
    arr = data['people'][0]['face_keypoints_2d']

    Dict = {}
    for i in range(70):
        j=i*3
        Dict[i] = [arr[j], 1-arr[j+1], arr[j+2]]

    return Dict

rigInfo = readRigInfo("C:\\Users\\ossya\\Downloads\\meshTestSampledFromSavedModelLandmarks_630.json")
        
keypoints = {}

for keypoint in rigInfo:
    keypoints[keypoint["id"]] = keypoint["coordinates"]

initial_model_pose = cf.parse_pose_25(cf.MAIN_DIR + '\\initialModelPose.json')
human_pose = cf.parse_pose_25(cf.MAIN_DIR + '\\human_keypoints.json')
face_pose = parse_face_80(cf.MAIN_DIR + '\\human_keypoints.json')

bones_map_Y = [['ShoulderLeft', 'LShoulder', 'LElbow'],
                 ['ShoulderRight', 'RShoulder', 'RElbow'],
                 ['ThighLeft', 'LHip', 'LKnee'],
                 ['ThighRight', 'RHip', 'RKnee']]
bones_map_elbow = [['HandLeft', 'LElbow', 'LWrist'],
                    ['HandRight', 'RElbow', 'RWrist']]


bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
obj = bpy.context.scene.objects["Armature"]

bpy.ops.object.select_all(action='DESELECT') # Deselect all objects
bpy.context.view_layer.objects.active = obj   # Make the cube the active object 
obj.select_set(True)

obj.rotation_euler.z += np.deg2rad(180)

bpy.ops.object.mode_set(mode='POSE', toggle=False)

scn = bpy.context.scene
bones = scn.objects['Armature'].pose.bones                   

for x1,x2,x3 in bones_map_Y:
    bones[x1].bone.select = True  
    
    angle_diff = cf.getAngle_2pts(human_pose[x2][:-1], human_pose[x3][:-1]) - cf.getAngle_2pts(initial_model_pose[x2][:-1], initial_model_pose[x3][:-1])
    bpy.ops.transform.rotate(value=angle_diff, orient_axis='Y', orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', constraint_axis=(False, True, False), mirror=False, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False, release_confirm=True)

    bones[x1].bone.select = False
    
for i,(x1,x2,x3) in enumerate(bones_map_elbow):
    bones[x1].bone.select = True  
    
    angle_diff = cf.getAngle_2pts(human_pose[x2][:-1], human_pose[x3][:-1]) - cf.getAngle_2pts(initial_model_pose[x2][:-1], initial_model_pose[x3][:-1])
    angle_diff_shoulder = cf.getAngle_2pts(human_pose[bones_map_Y[i][1]][:-1], human_pose[bones_map_Y[i][2]][:-1]) - cf.getAngle_2pts(initial_model_pose[bones_map_Y[i][1]][:-1], initial_model_pose[bones_map_Y[i][2]][:-1])
    angle_diff -= angle_diff_shoulder
    bpy.ops.transform.rotate(value=angle_diff, orient_axis='Y', orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', constraint_axis=(False, True, False), mirror=False, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False, release_confirm=True)

    bones[x1].bone.select = False
    

# Load a new image into the main database
image = bpy.data.images.load('C:/Users/ossya/Downloads/Oss.png', check_existing=False)

for item in scn.objects:
    if item.type == 'MESH':
        obj = item
        break

bpy.ops.object.mode_set(mode='OBJECT')
mesh = obj.data
vertices = mesh.vertices
dimensions = obj.dimensions

if not mesh.vertex_colors:
    mesh.vertex_colors.new()
    
color_layer = mesh.vertex_colors.active 

i = 0
minx= 1000000000
miny = 100000000

local_pixels = list(image.pixels[:])
for poly in mesh.polygons:
    for idx in poly.loop_indices:
        loop = mesh.loops[idx]
        v = loop.vertex_index
        
        if minx > vertices[v].co.x:
            minx = vertices[v].co.x
        if miny > vertices[v].co.y:
            miny = vertices[v].co.y

chin = keypoints['chin']  
head_top = keypoints['head.top']
#top of head color (hair)
xpos_h= math.floor(image.size[0] * (head_top[0] - minx)/ dimensions.x)
ypos_h= math.floor(image.size[1] * (head_top[1] - miny) / dimensions.y) - 1
index_h = ypos_h * 4* image.size [0] + xpos_h * 4
chin_in_image = face_pose[8]
face_left = face_pose[16]
face_right = face_pose[0]
face_width = math.floor(abs(face_right[0] - face_left[0]))
face_height = math.floor(abs(0 - chin_in_image[1]))
for poly in mesh.polygons:
    for idx in poly.loop_indices:
        loop = mesh.loops[idx]
        v = loop.vertex_index
        
        xpos= math.floor(image.size[0] * (vertices[v].co.x - minx)/ dimensions.x)
        ypos= math.floor(image.size[1] * (vertices[v].co.y - miny) / dimensions.y)
        index = ypos * 4* image.size [0] + xpos * 4
        
        if vertices[v].co.y >= chin[1] and vertices[v].co.z < head_top[2]:
            color_layer.data[i].color = (local_pixels[index_h], local_pixels[index_h + 1], local_pixels[index_h + 2], local_pixels[index_h + 3])
        elif vertices[v].co.y >= chin[1]: #front face
            xpos= math.floor(image.size[0] * (vertices[v].co.x - minx)/ dimensions.x)
            ypos= math.floor(image.size[1] - (face_height * (head_top[1] - vertices[v].co.y) / (head_top[1] - chin[1]))) - 1
            index = ypos * 4* image.size[0] + xpos * 4
            color_layer.data[i].color = (local_pixels[index], local_pixels[index + 1], local_pixels[index + 2], local_pixels[index + 3])
        else:
            color_layer.data[i].color = (local_pixels[index], local_pixels[index + 1], local_pixels[index + 2], local_pixels[index + 3])
        i += 1


bpy.ops.object.select_all(action='DESELECT') # Deselect all objects
bpy.context.view_layer.objects.active = obj   # Make the cube the active object 
obj.select_set(True)

bpy.context.scene.use_nodes = True
tree = obj.active_material.node_tree
prev_area = bpy.context.area.type
bpy.context.area.type = 'NODE_EDITOR'

# Get Vertex Color Node, create it if it does not exist in the current node tree
vertex_color_node = tree.nodes.get("Vertex Color")
if vertex_color_node == None:
    vertex_color_node = tree.nodes.new('ShaderNodeVertexColor')

bsdf = tree.nodes.get("Principled BSDF") 
tree.links.new(vertex_color_node.outputs['Color'], bsdf.inputs['Base Color'])

bpy.context.area.type = prev_area

bpy.ops.object.mode_set(mode='VERTEX_PAINT')