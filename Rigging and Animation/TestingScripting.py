import bpy
import json
import math
import pathlib
import mathutils
import numpy as np
from os import listdir
from mathutils import Matrix


class cf(): # common functions
    
    MAIN_DIR = str(pathlib.Path(__file__).parent.parent.resolve())
    
    @staticmethod
    def parse_pose_25(Dir):
        
        f = open(Dir)
        data = json.load(f)
        arr = data['people'][0]['pose_keypoints_2d']
        Map = ['Nose', 'Neck', 'RShoulder', 'RElbow' ,'RWrist', 'LShoulder',
               'LElbow', 'LWrist', 'MidHip', 'RHip', 'RKnee', 'RAnkle', 'LHip',
               'LKnee', 'LAnkle', 'REye', 'LEye', 'REar', 'LEar', 'LBigToe',
               'LSmallToe', 'LHeel', 'RBigToe', 'RSmallToe', 'RHeel']

        Dict = {}
        for i in range(25):
            j=i*3
            Dict[Map[i]] = [arr[j], 1-arr[j+1], arr[j+2]]
            
        return Dict

    @staticmethod
    def getAngle_2pts(p1, p2, degree=False):
        dx = p2[0] - p1[0]
        dy = p2[1] - p1[1]
        angle = math.atan2(dy, dx)
        
        if degree:
            angle = math.degrees(angle)
            
        return angle
    
    @staticmethod
    def getDistance_2pts(p1, p2):
        return math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)

    @staticmethod
    def getThighAngle(L1, L2, degree=False):
        angle = math.acos(L2/L1)
        if degree:
            angle = math.degrees(angle)
            
        return angle

class TestPanel(bpy.types.Panel):
    bl_label = "Test Panel"
    bl_idname = "PT_TestPanel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Test Panel"

    def draw(self, context):
       self.layout.operator("mesh.import_model", icon='MESH_CUBE', text="Import Model")
       self.layout.operator("mesh.delete_model", icon='MESH_CUBE', text="Delete Model")           
       self.layout.operator("mesh.apply_ik", icon='GIZMO', text="Apply IK")  
       self.layout.operator("mesh.animate", icon='MESH_CUBE', text="Animate") 

class animate(bpy.types.Operator):
    bl_idname = 'mesh.animate'
    bl_label = 'Animate'
    bl_options = {"REGISTER", "UNDO"}
 
    def execute(self, context):
        
        bones_map_Y = [['ShoulderLeft', 'LShoulder', 'LElbow'],
                     ['ShoulderRight', 'RShoulder', 'RElbow'],
                     ['ThighLeft', 'LHip', 'LKnee'],
                     ['ThighRight', 'RHip', 'RKnee'],
                     ['SpinalCordB4', 'Nose', 'Neck']]
                     
        # loading pose file names sorted
        list_json = [f for f in sorted(listdir(cf.MAIN_DIR + '\\pose_ex\\')) if (str(f))[-4:] == "json"]
        frames = []
        for file_name in list_json:
            frames.append(cf.parse_pose_25(cf.MAIN_DIR + '\\pose_ex\\' + file_name))
        
                     
        # TODO: Frame 0 (intial model state) -> Frame 1 (intial animation state)
        fps = 2
        
        scn = bpy.context.scene
        bpy.ops.object.mode_set(mode='POSE', toggle=False)
        bones = scn.objects['Armature'].pose.bones
        scn.frame_start = 1
        scn.frame_end = (len(frames)-1)*(24//fps) + 1

            
        for frame_num in range(len(frames)):
            for x in ['LegLeft', 'LegRight']:
                bones[x].bone.select = True
                bpy.context.scene.frame_set((frame_num)*(24//fps) + 1)
                bpy.ops.anim.keyframe_insert_menu(type='Rotation')
                bones[x].bone.select = False
        
        for x1,_,_ in bones_map_Y:
            bones[x1].bone.select = True
            bpy.context.scene.frame_set(1)
            bpy.ops.anim.keyframe_insert_menu(type='Rotation')
            bones[x1].bone.select = False
            
        # XZ plane Animation
        for frame_num in range(len(frames)-1):
            for x1,x2,x3 in bones_map_Y:
                
                bones[x1].bone.select = True  
                bpy.context.scene.frame_set((frame_num+1)*(24//fps) + 1)
                
                angel_diff = cf.getAngle_2pts(frames[frame_num+1][x2][:-1], frames[frame_num+1][x3][:-1]) - cf.getAngle_2pts(frames[frame_num][x2][:-1], frames[frame_num][x3][:-1])
                bpy.ops.transform.rotate(value=angel_diff, orient_axis='Y', orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', constraint_axis=(False, True, False), mirror=False, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False, release_confirm=True)

                bpy.ops.anim.keyframe_insert_menu(type='Rotation')
                bones[x1].bone.select = False
                
        # legs (to front) Animation
        thighAngleThreshold = 0.6
        
        # bones_map_X = [bone in armature, point 1 in pose, point 2 in pose, rotation direction, max length, is child flag]
        bones_map_X = [['ThighLeft', 'LHip', 'LKnee', 1, 0, False], 
                        ['LegLeft', 'LKnee', 'LAnkle', -1, 0, True],
                        ['ThighRight', 'RHip', 'RKnee', 1, 0, False],
                        ['LegRight', 'RKnee', 'RAnkle', -1, 0, True]]
        
        for frame_num in range(len(frames)):
            for i in range(len(bones_map_X)):
                bone_length = cf.getDistance_2pts(frames[frame_num][bones_map_X[i][1]][:-1], frames[frame_num][bones_map_X[i][2]][:-1])
                if bone_length > bones_map_X[i][4]: bones_map_X[i][4] = bone_length

        perant_angle = 0
        for frame_num in range(1,len(frames)):
            for i in range(len(bones_map_X)):
                bone_length = cf.getDistance_2pts(frames[frame_num][bones_map_X[i][1]][:-1], frames[frame_num][bones_map_X[i][2]][:-1])
                Angle = cf.getThighAngle(bones_map_X[i][4], bone_length)
                if bones_map_X[i][5]: Angle -= perant_angle/2 # only subtracting it's half as when the thigh is pushed forward same goes for the shin, it gets nearer to the camera and appears longer in the pose values
                print(bones_map_X[i][0], ': ', Angle)
                
                Angle = 0 if Angle < 0 else Angle
            
                if Angle > thighAngleThreshold: 
                    bones[bones_map_X[i][0]].bone.select = True
                    bpy.context.scene.frame_set((frame_num)*(24//fps) + 1)
                    bpy.ops.transform.rotate(value=Angle * bones_map_X[i][3], orient_axis='X', orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', constraint_axis=(True, False, False), mirror=False, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False, release_confirm=True)
                    bpy.ops.anim.keyframe_insert_menu(type='Rotation')
                    bones[bones_map_X[i][0]].bone.select = False
                    
                perant_angle = Angle
                
        
        return {"FINISHED"}


class applyIK(bpy.types.Operator):
    bl_idname = 'mesh.apply_ik'
    bl_label = 'Apply IK'
    bl_options = {"REGISTER", "UNDO"}
 
    def normalize(self, vect):
        val = np.array(vect)
        return val / np.linalg.norm(val)
 
    def execute(self, context):
        
        '''
        selected_ob = bpy.data.objects['Armature']
        
        if selected_ob != None:
            bpy.ops.object.mode_set(mode='POSE', toggle=False)
            bones = selected_ob.pose.bones
        
            fistLeft = bones["FistLeft"] #target
            handLeft = bones["HandLeft"]
            shoulderLeft = bones["ShoulderLeft"]
            
            #applying FABRIK algorithm
            noOfIterations = 15
            convergenceDist = 0.001 #depends on the size of the model
            
            print(handLeft.head)
            distBetweenBones = np.linalg.norm(np.array(shoulderLeft.tail) - np.array(handLeft.head))
            totalArmLength = handLeft.length + shoulderLeft.length + distBetweenBones
            
            areBonesExtended = totalArmLength <= np.linalg.norm(np.array(shoulderLeft.head) - np.array(fistLeft.head))
            
            #bpy.ops.object.mode_set(mode='POSE', toggle=False)
            
            #bpy.ops.transform.rotate(value=3.14 / 2.0, orient_axis='X', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)))
            if areBonesExtended: #stretch bones
                
                #bpy.ops.object.mode_set(mode='EDIT', toggle=False)
                #selected_ob.data.edit_bones["FistLeft"].parent = None
                #bpy.ops.object.mode_set(mode='POSE', toggle=False)

                # Left Shoulder
                v = fistLeft.head - shoulderLeft.head
                bv = shoulderLeft.tail - shoulderLeft.head

                rd = bv.rotation_difference(v)

                M = (
                    Matrix.Translation(shoulderLeft.head) @
                    rd.to_matrix().to_4x4() @
                    Matrix.Translation(-shoulderLeft.head)
                )
                shoulderLeft.matrix = M @ shoulderLeft.matrix
                
                # Left Hand
                v = fistLeft.head - shoulderLeft.head
                bv = shoulderLeft.tail - shoulderLeft.head

                rd = bv.rotation_difference(v)

                M = (
                    Matrix.Translation(shoulderLeft.head) @
                    rd.to_matrix().to_4x4() @
                    Matrix.Translation(-shoulderLeft.head)
                )
                shoulderLeft.matrix = M @ shoulderLeft.matrix
        '''
        
        scn = bpy.context.scene
        bpy.ops.object.mode_set(mode='POSE', toggle=False)
        bones = scn.objects['Armature'].pose.bones
        bones["ShoulderLeft"].bone.select = True
        
        scn.frame_start = 1
        scn.frame_end = 120
        bpy.context.scene.frame_set(1)
        bpy.ops.anim.keyframe_insert_menu(type='Rotation')
        bpy.context.scene.frame_set(100)
        bpy.ops.transform.rotate(value=-1.42241, orient_axis='Y', orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', constraint_axis=(False, True, False), mirror=True, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False, release_confirm=True)
        bpy.ops.anim.keyframe_insert_menu(type='Rotation')

        bones["ShoulderLeft"].bone.select = False
        bones["HandLeft"].bone.select = True
        
        bpy.context.scene.frame_set(1)
        bpy.ops.anim.keyframe_insert_menu(type='Rotation')
        bpy.context.scene.frame_set(100)
        bpy.ops.transform.rotate(value=-1.58124, orient_axis='Y', orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', constraint_axis=(False, True, False), mirror=True, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False, release_confirm=True)
        bpy.ops.transform.rotate(value=-1.05258, orient_axis='Z', orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', constraint_axis=(False, False, True), mirror=True, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False, release_confirm=True)
        bpy.ops.anim.keyframe_insert_menu(type='Rotation')
        
        bones["HandLeft"].bone.select = False
        bones["FistLeft"].bone.select = True
        
        bpy.context.scene.frame_set(1)
        bpy.ops.anim.keyframe_insert_menu(type='Rotation')
        bpy.context.scene.frame_set(100)
        bpy.ops.transform.rotate(value=-1.39506, orient_axis='Z', orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', constraint_axis=(False, False, True), mirror=True, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False, release_confirm=True)
        bpy.ops.transform.rotate(value=-1.21232, orient_axis='Y', orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', constraint_axis=(False, True, False), mirror=True, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False, release_confirm=True)
        bpy.ops.anim.keyframe_insert_menu(type='Rotation')
        
        bpy.ops.object.posemode_toggle()            
                
        return {"FINISHED"}
    
    
class deleteModel(bpy.types.Operator):
    bl_idname = 'mesh.delete_model'
    bl_label = 'Delete Model'
    bl_options = {"REGISTER", "UNDO"}
    
    def execute(self, context):
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete()
        
        return {"FINISHED"}
    
        
class addReggedModel(bpy.types.Operator):
    bl_idname = 'mesh.import_model'
    bl_label = 'Import Model'
    bl_options = {"REGISTER", "UNDO"}
    
    def readRigInfo(self, fileName):
        with open(fileName, "r") as read_file:
            rigInfo = json.load(read_file)
        
        return rigInfo
    
    def import_model(context):
        bpy.ops.import_mesh.stl(filepath = (str(pathlib.Path(__file__).parent.parent.resolve()) + "\\Mesh.stl"))
        
    def add_armature(context,self):
        model = bpy.context.active_object #get the armature object
        print(model.name)
        print(model.location)
        bpy.ops.object.add(type = "ARMATURE")
        
        obArm = bpy.context.active_object #get the armature object
        obArm.location = model.location
        obArm.rotation_euler = model.rotation_euler
        bpy.ops.object.mode_set(mode='EDIT', toggle=False)
        ebs = obArm.data.edit_bones

        rigInfo = self.readRigInfo((str(pathlib.Path(__file__).parent.parent.resolve()) + "\\RigInfo.json"))
        
        keypoints = {}
        
        for keypoint in rigInfo:
            keypoints[keypoint["id"]] = keypoint["coordinates"]
          
        #Spinal Cord
        spinalCordBone1 = ebs.new("SpinalCordB1")
        spinalCordBone1.head = mathutils.Vector(np.array((keypoints["pampers.front"]) + np.array(keypoints["pampers.back"])) / 2)
        spinalCordBone1.tail = mathutils.Vector(np.array((keypoints["belly.right"]) + np.array(keypoints["belly.left"])) / 2)
        
        spinalCordBone2 = ebs.new("SpinalCordB2")
        neckBone = mathutils.Vector(np.array((keypoints["neckstart.front.center"]) + np.array(keypoints["neckstart.back.center"])) / 2)
        auxHeadBone = mathutils.Vector(np.array((keypoints["head.front"]) + np.array(keypoints["head.back"])) / 2)
        auxNeckPoint = np.array(np.array(auxHeadBone) + np.array(neckBone)) / 2
        spinalCordBone2.head = spinalCordBone1.tail
        spinalCordBone2.tail = mathutils.Vector(np.array(auxNeckPoint + np.array(neckBone)) / 2)
        spinalCordBone2.tail = mathutils.Vector(np.array(np.array(neckBone) + np.array(spinalCordBone2.tail)) / 2)
        spinalCordBone2.tail = mathutils.Vector(np.array(np.array(neckBone) + np.array(spinalCordBone2.tail)) / 2)
        spinalCordBone2.select = True
        spinalCordBone2.parent = spinalCordBone1
        bpy.ops.armature.subdivide(number_cuts=2)
        spinalCordBone2.select = False
        spinalCordBone2.children[0].select = False
        spinalCordBone2.children[0].children[0].select = False
        
        #Head 
        headBone = ebs.new("HeadBone")
        boneMagnitude = math.sqrt(sum(i**2 for i in (np.array(keypoints["head.front"]) - np.array(keypoints["chin"]))))
        headBone.head = mathutils.Vector(np.array((keypoints["head.front"]) + np.array(keypoints["head.back"])) / 2)# if the head and tail are the same, the bone is deleted
        headBone.tail = keypoints["head.top"]
        headBoneDirection = (np.array(headBone.tail) - np.array(headBone.head)) / math.sqrt(sum(i**2 for i in (np.array(headBone.tail) - np.array(headBone.head))))
        headBone.head = mathutils.Vector(np.array(headBone.tail) - boneMagnitude * headBoneDirection)
        #headBone.use_connect = True
        
        spinalCordBone4 = ebs.new("SpinalCordB4")
        spinalCordBone4.head = spinalCordBone2.children[0].children[0].tail
        spinalCordBone4.tail = headBone.head
        spinalCordBone4.select = True
        spinalCordBone4.parent = spinalCordBone2.children[0].children[0]
        bpy.ops.armature.subdivide()
        spinalCordBone4.select = False
        spinalCordBone4.children[0].select = False
        #spinalCordBone4.use_connect = True
        
        headBone.parent = spinalCordBone4.children[0]
        
        #right thigh
        thighRightBone = ebs.new("ThighRight")
        waistCenter = np.array((keypoints["waist.front.center"]) + np.array(keypoints["waist.back.center"])) / 2
        thighRightBone.head = mathutils.Vector((waistCenter + np.array(keypoints["waist.right"])) / 2)
        thighRightBone.tail = mathutils.Vector(np.array((keypoints["knee.right.front"]) + np.array(keypoints["knee.right.back"])) / 2)
        thighRightBone.parent = spinalCordBone1
        #thighRightBone.use_connect = True
        
        #right leg
        legRightBone = ebs.new("LegRight")
        legRightBone.head = thighRightBone.tail
        legRightBone.tail = mathutils.Vector(np.array((keypoints["ankle.right.inside"]) + np.array(keypoints["ankle.right.outside"])) / 2)
        legRightBone.parent = thighRightBone
        #legRightBone.use_connect = True
        
        #right foot
        footRightBone = ebs.new("footRight")
        footRightBone.head = legRightBone.tail
        footRightBone.tail = keypoints["foot.right.bottom.center"]
        footRightBone.parent = legRightBone
        #footRightBone.use_connect = True
        
        #left thigh
        thighLeftBone = ebs.new("ThighLeft")
        thighLeftBone.head = mathutils.Vector((waistCenter + np.array(keypoints["waist.left"])) / 2)
        thighLeftBone.tail = mathutils.Vector(np.array((keypoints["knee.left.front"]) + np.array(keypoints["knee.left.back"])) / 2)
        thighLeftBone.parent = spinalCordBone1
        #thighLeftBone.use_connect = True
        
        #lef leg
        legLeftBone = ebs.new("LegLeft")
        legLeftBone.head = thighLeftBone.tail
        legLeftBone.tail = mathutils.Vector(np.array((keypoints["ankle.left.inside"]) + np.array(keypoints["ankle.left.outside"])) / 2)
        legLeftBone.parent = thighLeftBone
        #legLeftBone.use_connect = True
        
        #left foot
        footLeftBone = ebs.new("footLeft")
        footLeftBone.head = legLeftBone.tail
        footLeftBone.tail = keypoints["foot.left.bottom.center"]
        footLeftBone.parent = legLeftBone
        #footLeftBone.use_connect = True
        
        #right shoulder
        #right shoulder bone
        upperShoulderRightBone = ebs.new("ShoulderRightBone")
        upperShoulderRightBone.head = keypoints["neckstart.front.center"]
        midShoulderBone = np.array((keypoints["shoulder.right.front"]) + np.array(keypoints["shoulder.right.back"])) / 2
        upperShoulderRightBone.tail = mathutils.Vector(np.array((keypoints["shoulder.right.top"]) + midShoulderBone) / 2)
        upperShoulderRightBone.parent = spinalCordBone2.children[0].children[0]
        #upperShoulderRightBone.use_connect = True
        
        shoulderRightBone = ebs.new("ShoulderRight")
        shoulderRightBone.head = mathutils.Vector(np.array((keypoints["shoulder.right.front"]) + np.array(keypoints["shoulder.right.back"])) / 2)
        shoulderRightBone.tail = mathutils.Vector(np.array((keypoints["elbow.right"]) + np.array(keypoints["midhand.right.center"])) / 2)
        shoulderRightBone.parent = upperShoulderRightBone
        #shoulderRightBone.use_connect = True
        
        handRightBone = ebs.new("HandRight")
        handRightBone.head = shoulderRightBone.tail
        handRightBone.tail = mathutils.Vector(np.array((keypoints["wrist.right.front"]) + np.array(keypoints["wrist.right.back"])) / 2)
        handRightBone.parent = shoulderRightBone
        #handRightBone.use_connect = True
        
        fistRightBone = ebs.new("FistRight")
        fistRightBone.head = handRightBone.tail 
        fistRightBone.tail = keypoints["fist.right.fist"]
        fistRightBone.parent = handRightBone
        #fistRightBone.use_connect = True
        
        #left shoulder
        #left shoulder bone
        upperShoulderLeftBone = ebs.new("ShoulderLeftBone")
        upperShoulderLeftBone.head = keypoints["neckstart.front.center"]
        midShoulderBoneLeft = midShoulderBone = np.array((keypoints["shoulder.left.front"]) + np.array(keypoints["shoulder.left.back"])) / 2
        upperShoulderLeftBone.tail = mathutils.Vector(np.array((keypoints["shoulder.left.top"]) + midShoulderBoneLeft) / 2)
        upperShoulderLeftBone.parent = spinalCordBone2.children[0].children[0]
        #upperShoulderLeftBone.use_connect = True
        
        shoulderLeftBone = ebs.new("ShoulderLeft")
        shoulderLeftBone.head = mathutils.Vector(np.array((keypoints["shoulder.left.front"]) + np.array(keypoints["shoulder.left.back"])) / 2)
        shoulderLeftBone.tail = mathutils.Vector(np.array((keypoints["elbow.left"]) + np.array(keypoints["midhand.left.center"])) / 2)
        shoulderLeftBone.parent = upperShoulderLeftBone
        #shoulderLeftBone.use_connect = True
        
        handLeftBone = ebs.new("HandLeft")
        handLeftBone.head = shoulderLeftBone.tail
        handLeftBone.tail = mathutils.Vector(np.array((keypoints["wrist.left.front"]) + np.array(keypoints["wrist.left.back"])) / 2)
        handLeftBone.parent = shoulderLeftBone
        #handLeftBone.use_connect = True
        
        fistLeftBone = ebs.new("FistLeft")
        fistLeftBone.head = handLeftBone.tail 
        fistLeftBone.tail = keypoints["fist.left.fist"]
        fistLeftBone.parent = handLeftBone
        #fistLeftBone.use_connect = True

        #Right Pelvis
        rightPelvisBone = ebs.new("RightPelvis")
        rightPelvisBone.head = mathutils.Vector(np.array((keypoints["pampers.front"]) + np.array(keypoints["pampers.back"])) / 2)
        auxPointPelvisRight = np.array((keypoints["belly.front.center"]) + np.array(keypoints["belly.right"])) / 2
        rightPelvisBone.tail = mathutils.Vector((auxPointPelvisRight + np.array(keypoints["belly.right"])) / 2)
        rightPelvisBone.parent = spinalCordBone1
        #rightPelvisBone.use_connect = True
        
        #Left Pelvis
        leftPelvisBone = ebs.new("LeftPelvis")
        leftPelvisBone.head = rightPelvisBone.head
        auxPointPelvisLeft = np.array((keypoints["belly.front.center"]) + np.array(keypoints["belly.left"])) / 2
        leftPelvisBone.tail = mathutils.Vector((auxPointPelvisLeft + np.array(keypoints["belly.left"])) / 2)
        leftPelvisBone.parent = spinalCordBone1
        #leftPelvisBone.use_connect = True
        
        #parenting of rig and model with automatic weights
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        model.select_set(True)
        obArm.select_set(True)
        bpy.context.view_layer.objects.active = obArm
        bpy.ops.object.parent_set(type='ARMATURE_AUTO')
        model.select_set(False)
        obArm.select_set(False)
        
        #connect corresponding bones together
        #eb2.parent = eb
        #eb2.use_connect = True
        
        
    def recenter(context):
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        
        obj = bpy.context.scene.objects["Armature"]
        obj.rotation_euler.x -= np.deg2rad(91.5)
        obj.rotation_euler.y += np.deg2rad(3)
        obj.rotation_euler.z += np.deg2rad(233)
        obj.location.z += 2
        obj.scale.x += 1
        obj.scale.y += 1
        obj.scale.z += 1

        bpy.ops.object.mode_set(mode='POSE', toggle=False)
 
    def execute(self, context):
        self.import_model()
        self.add_armature(self)
        self.recenter()
        
        return {"FINISHED"}


def register() :
    bpy.utils.register_class(TestPanel)
    bpy.utils.register_class(addReggedModel)
    bpy.utils.register_class(deleteModel)
    bpy.utils.register_class(applyIK)
    bpy.utils.register_class(animate)
 
def unregister() :
    bpy.utils.unregister_class(TestPanel)
    bpy.utils.unregister_class(addReggedModel)
    bpy.utils.unregister_class(deleteModel)
    bpy.utils.unregister_class(applyIK)
    bpy.utils.unregister_class(animate)
    
if __name__ == "__main__":
    register()