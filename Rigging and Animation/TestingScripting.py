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
    def load_frames_pose(Dir_pose = '\\frames\\pose\\', fps_rounded=True):     
        list_json_raw = listdir(cf.MAIN_DIR + Dir_pose)
        list_json = [('frame' + str(i+1) + '_keypoints.json') for i in range(len(list_json_raw)-1) if (str(list_json_raw[i]))[-4:] == "json"]
        frames = []
        for file_name in list_json:
            if cf.people_count_in_file(cf.MAIN_DIR + Dir_pose + file_name) == 1:
                frames.append(cf.parse_pose_25(cf.MAIN_DIR + Dir_pose + file_name))
            else:
                frames.append(frames[-1])

        f = open(cf.MAIN_DIR + Dir_pose + '\\my_fps.txt')
        fps = f.read()
        fps = float(fps)
        f.close()

        cf.fix_unseen_joints(frames)

        if fps_rounded: 
            fps = round(fps)
        
        return frames, fps
    
    @staticmethod
    def people_count_in_file(Dir):
        f = open(Dir)
        data = json.load(f)
        arr = data['people']
        return len(arr)
    

    @staticmethod
    def fix_unseen_joints(frames):
        # TODO: make it more general
        for i in range(len(frames)):
            for joint in cf.JOINTS_MAP:
                if frames[i][joint][-1] == 0:
                    frames[i][joint] = frames[i-1][joint]
                    frames[i][joint][-1] = 0
        return frames

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
    def getDepthAngle(L1, L2, degree=False):
        if L2/L1 > 1:
            return 0
        
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
       self.layout.operator("mesh.animate", icon='MESH_CUBE', text="Animate") 
       self.layout.operator("mesh.test", icon='MESH_CUBE', text="Test") 
       
class test(bpy.types.Operator):
    bl_idname = 'mesh.test'
    bl_label = 'Test'
    bl_options = {"REGISTER", "UNDO"}
    
    def execute(self, context):
        scn = bpy.context.scene
        bpy.ops.object.mode_set(mode='POSE', toggle=False)
        bones = scn.objects['Armature'].pose.bones
        
        angle_left = cf.getAngle_2pts(list(bones['ThighLeft'].head)[:-1], list(bones['ThighLeft'].tail)[:-1])
                
        print('angle_left:', np.rad2deg(angle_left))
        
        
        return {"FINISHED"}

class animate(bpy.types.Operator):
    bl_idname = 'mesh.animate'
    bl_label = 'Animate'
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        
        initial_frame = cf.parse_pose_25(cf.MAIN_DIR + '\\initialModelPose.json')
        bones_map_Y = [['ShoulderLeft', 'LShoulder', 'LElbow'],
                         ['ShoulderRight', 'RShoulder', 'RElbow'],
                         ['ThighLeft', 'LHip', 'LKnee'],
                         ['ThighRight', 'RHip', 'RKnee']]
        bones_map_elbow = [['HandLeft', 'LElbow', 'LWrist'],
                            ['HandRight', 'RElbow', 'RWrist']]

        # loading frames and downsampled fps
        frames, fps = cf.load_frames_pose()

        scn = bpy.context.scene
        bpy.ops.object.mode_set(mode='POSE', toggle=False)
        bones = scn.objects['Armature'].pose.bones
        scn.frame_start = 0 
        scn.frame_end = (len(frames)-1)*(24//fps) + 1


        ###################################################################
        ####### Saving some bones rotation in frames  #####################
        ###################################################################
        for x in ['LegLeft', 'LegRight', 'SpinalCordB4', 'ShoulderLeftBone', 'ShoulderRightBone', 'ThighLeft', 'ThighRight']:
            for frame_num in range(len(frames)):
                bones[x].bone.select = True
                bpy.context.scene.frame_set(frame_num*(24//fps))
                bpy.ops.anim.keyframe_insert_menu(type='Rotation')
                bones[x].bone.select = False
        ###################################################################
        
        ###################################################################
        ####### Translating the models initial pose to frame 1 pose #######
        ###################################################################
        bpy.context.scene.frame_set(0)
        
        for x1,x2,x3 in bones_map_Y:
            bones[x1].bone.select = True  
            angle_diff = cf.getAngle_2pts(frames[0][x2][:-1], frames[0][x3][:-1]) - cf.getAngle_2pts(initial_frame[x2][:-1], initial_frame[x3][:-1])
            bpy.ops.transform.rotate(value=angle_diff, orient_axis='Y', orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', constraint_axis=(False, True, False), mirror=False, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False, release_confirm=True)
            bpy.ops.anim.keyframe_insert_menu(type='Rotation')
            bones[x1].bone.select = False
        
        for i,(x1,x2,x3) in enumerate(bones_map_elbow):
            bones[x1].bone.select = True  
            angle_diff_elbow = cf.getAngle_2pts(frames[0][x2][:-1], frames[0][x3][:-1]) - cf.getAngle_2pts(initial_frame[x2][:-1], initial_frame[x3][:-1])
            angle_diff_shoulder = cf.getAngle_2pts(frames[0][bones_map_Y[i][1]][:-1], frames[0][bones_map_Y[i][2]][:-1]) - cf.getAngle_2pts(initial_frame[bones_map_Y[i][1]][:-1], initial_frame[bones_map_Y[i][2]][:-1])
            angle_diff_elbow -= angle_diff_shoulder
            bpy.ops.transform.rotate(value=angle_diff_elbow, orient_axis='Y', orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', constraint_axis=(False, True, False), mirror=False, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False, release_confirm=True)
            bpy.ops.anim.keyframe_insert_menu(type='Rotation')
            bones[x1].bone.select = False
        ###################################################################

        
        ###################################################################
        ####### XZ plane Arm Animation ####################################
        ###################################################################
        x1_l,x2_l,x3_l,x4_l,x5_l = ['ShoulderLeft', 'LShoulder', 'LElbow', 'ShoulderLeftBone', -1]
        x1_r,x2_r,x3_r,x4_r,x5_r = ['ShoulderRight', 'RShoulder', 'RElbow', 'ShoulderRightBone', 1]
        x1_r_e,x2_r_e,x3_r_e = ['HandRight', 'RElbow', 'RWrist']
        x1_l_e,x2_l_e,x3_l_e = ['HandLeft', 'LElbow', 'LWrist']
                            
        arm_angle_threshold_l = -87
        arm_angle_threshold_r = -93        

        raised_r, raised_l = False, False
        
        for frame_num in range(len(frames)-1):
            
            bpy.context.scene.frame_set((frame_num+1)*(24//fps))
            
            ####### Left Arm Animation ########################################
            
            angle_diff_shoulder_l = cf.getAngle_2pts(frames[frame_num+1][x2_l][:-1], frames[frame_num+1][x3_l][:-1]) - cf.getAngle_2pts(frames[frame_num][x2_l][:-1], frames[frame_num][x3_l][:-1])            
            angle_model = cf.getAngle_2pts(list(bones[x1_l].head)[:-1], list(bones[x1_l].tail)[:-1]) 
            
            ####### Left Elbow Animation #####################
            bones[x1_l_e].bone.select = True  
            
            angle_diff_elbow_l = cf.getAngle_2pts(frames[frame_num+1][x2_l_e][:-1], frames[frame_num+1][x3_l_e][:-1]) - cf.getAngle_2pts(frames[frame_num][x2_l_e][:-1], frames[frame_num][x3_l_e][:-1])
            angle_diff_elbow_l -= angle_diff_shoulder_l
            bpy.ops.transform.rotate(value=angle_diff_elbow_l, orient_axis='Y', orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', constraint_axis=(False, True, False), mirror=False, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False, release_confirm=True)
                
            bpy.ops.anim.keyframe_insert_menu(type='Rotation')
            bones[x1_l_e].bone.select = False
            ##################################################
            
            left_forearm_angle = cf.getAngle_2pts(list(bones[x1_l_e].head)[:-1], list(bones[x1_l_e].tail)[:-1])

            if np.rad2deg(left_forearm_angle + angle_diff_shoulder_l) < arm_angle_threshold_l and not raised_l: 
                
                bones[x1_l].bone.select = True 
                bpy.ops.transform.rotate(value=0.4, orient_axis='X', orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', constraint_axis=(True, False, False), mirror=False, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False, release_confirm=True)
                bpy.ops.anim.keyframe_insert_menu(type='Rotation')
                bones[x1_l].bone.select = False
                
                bones[x4_l].bone.select = True 
                bpy.ops.transform.rotate(value=0.4*x5_l, orient_axis='Z', orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', constraint_axis=(False, False, True), mirror=False, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False, release_confirm=True)
                bpy.ops.anim.keyframe_insert_menu(type='Rotation')
                bones[x4_l].bone.select = False
                
                raised_l = True
                
            elif np.rad2deg(left_forearm_angle + angle_diff_shoulder_l) < arm_angle_threshold_l and raised_l:
                bones[x4_l].bone.select = True 
                bpy.ops.transform.rotate(value=0.4*x5_l, orient_axis='Z', orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', constraint_axis=(False, False, True), mirror=False, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False, release_confirm=True)
                bpy.ops.anim.keyframe_insert_menu(type='Rotation')
                bones[x4_l].bone.select = False
            
            elif np.rad2deg(left_forearm_angle + angle_diff_shoulder_l) > arm_angle_threshold_l and raised_l:
                bones[x1_l].bone.select = True 
                bpy.ops.transform.rotate(value=-0.4, orient_axis='X', orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', constraint_axis=(True, False, False), mirror=False, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False, release_confirm=True)
                bpy.ops.anim.keyframe_insert_menu(type='Rotation')
                bones[x1_l].bone.select = False
                
                raised_l = False
            
            bones[x1_l].bone.select = True  
            bpy.ops.transform.rotate(value=angle_diff_shoulder_l, orient_axis='Y', orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', constraint_axis=(False, True, False), mirror=False, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False, release_confirm=True)
            bpy.ops.anim.keyframe_insert_menu(type='Rotation')
            bones[x1_l].bone.select = False
            
            
            ####### Right Arm Animation ########################################        
            
            angle_diff_shoulder_r = cf.getAngle_2pts(frames[frame_num+1][x2_r][:-1], frames[frame_num+1][x3_r][:-1]) - cf.getAngle_2pts(frames[frame_num][x2_r][:-1], frames[frame_num][x3_r][:-1])
            angle_model = cf.getAngle_2pts(list(bones[x1_r].head)[:-1], list(bones[x1_r].tail)[:-1])
            
            ####### Right Elbow Animation ####################
            bones[x1_r_e].bone.select = True 
            
            right_shoulder_angle = cf.getAngle_2pts(list(bones[x1_r].head)[:-1], list(bones[x1_r].tail)[:-1]) 

            angle_diff_elbow_r = cf.getAngle_2pts(frames[frame_num+1][x2_r_e][:-1], frames[frame_num+1][x3_r_e][:-1]) - cf.getAngle_2pts(frames[frame_num][x2_r_e][:-1], frames[frame_num][x3_r_e][:-1])
            angle_diff_elbow_r -= angle_diff_shoulder_r
            bpy.ops.transform.rotate(value=angle_diff_elbow_r, orient_axis='Y', orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', constraint_axis=(False, True, False), mirror=False, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False, release_confirm=True)
            bpy.ops.anim.keyframe_insert_menu(type='Rotation')
            bones[x1_r_e].bone.select = False
            ##################################################
            
            right_forearm_angle = cf.getAngle_2pts(list(bones[x1_r_e].head)[:-1], list(bones[x1_r_e].tail)[:-1])

            if np.rad2deg(right_forearm_angle + angle_diff_shoulder_r) > arm_angle_threshold_r and np.rad2deg(right_forearm_angle + angle_diff_shoulder_r) < 0 and not raised_r:
                bones[x1_r].bone.select = True 
                bpy.ops.transform.rotate(value=0.4, orient_axis='X', orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', constraint_axis=(True, False, False), mirror=False, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False, release_confirm=True)
                bpy.ops.anim.keyframe_insert_menu(type='Rotation')
                bones[x1_r].bone.select = False
                
                bones[x4_r].bone.select = True 
                bpy.ops.transform.rotate(value=0.4*x5_r, orient_axis='Z', orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', constraint_axis=(False, False, True), mirror=False, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False, release_confirm=True)
                bpy.ops.anim.keyframe_insert_menu(type='Rotation')
                bones[x4_r].bone.select = False
                
                raised_r = True
                
            elif np.rad2deg(right_forearm_angle + angle_diff_shoulder_r) > arm_angle_threshold_r and np.rad2deg(right_forearm_angle + angle_diff_shoulder_r) < 0 and raised_r:
                bones[x4_r].bone.select = True 
                bpy.ops.transform.rotate(value=0.4*x5_r, orient_axis='Z', orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', constraint_axis=(False, False, True), mirror=False, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False, release_confirm=True)
                bpy.ops.anim.keyframe_insert_menu(type='Rotation')
                bones[x4_r].bone.select = False
            
            elif (np.rad2deg(right_forearm_angle + angle_diff_shoulder_r) < arm_angle_threshold_r or np.rad2deg(right_forearm_angle + angle_diff_shoulder_r) > 0) and raised_r:
                bones[x1_r].bone.select = True 
                bpy.ops.transform.rotate(value=-0.4, orient_axis='X', orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', constraint_axis=(True, False, False), mirror=False, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False, release_confirm=True)
                bpy.ops.anim.keyframe_insert_menu(type='Rotation')
                bones[x1_r].bone.select = False
                
                raised_r = False
                
            bones[x1_r].bone.select = True
            bpy.ops.transform.rotate(value=angle_diff_shoulder_r, orient_axis='Y', orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', constraint_axis=(False, True, False), mirror=False, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False, release_confirm=True)
            bpy.ops.anim.keyframe_insert_menu(type='Rotation')
            bones[x1_r].bone.select = False
        ###################################################################

        
        
        ###################################################################
        ####### legs (to front& back) Animation ###########################
        ###################################################################
        thighAngleThreshold = math.radians(20)
        include_knees_depth = False
        
        # bones_map_legs = [bone in armature, point 1 in pose, point 2 in pose, rotation direction, max length, is child flag]
        bones_map_legs = [['ThighLeft', 'LHip', 'LKnee', 1, 0, False], 
                        ['LegLeft', 'LKnee', 'LAnkle', -1, 0, True],
                        ['ThighRight', 'RHip', 'RKnee', 1, 0, False],
                        ['LegRight', 'RKnee', 'RAnkle', -1, 0, True]]
        leg_moved_forward = {bones_map_legs[0][0]: [False for _ in range(len(frames))],\
                             bones_map_legs[2][0]: [False for _ in range(len(frames))]}
        
        # Calculating leg bones lengths
        for i in range(len(bones_map_legs)):
            if not include_knees_depth and bones_map_legs[i][-1]:
                continue
                
            bone_lengths = []
            for frame_num in range(len(frames)):
                bone_length = cf.getDistance_2pts(frames[frame_num][bones_map_legs[i][1]][:-1], frames[frame_num][bones_map_legs[i][2]][:-1])
                bone_lengths.append(bone_length)
            
            bone_lengths.sort(reverse=True)
            bones_map_legs[i][4] = sum(bone_lengths[: len(frames)//2]) / (len(frames)//2)

        
        
        for frame_num in range(1,len(frames)):
            perant_angle = 0
            
            # Checking if both legs will be raised
            bone_length_left_thigh = cf.getDistance_2pts(frames[frame_num]['LHip'][:-1], frames[frame_num]['LKnee'][:-1])
            angle_left_thigh = cf.getDepthAngle(bones_map_legs[0][4], bone_length_left_thigh)
            bone_length_right_thigh = cf.getDistance_2pts(frames[frame_num]['RHip'][:-1], frames[frame_num]['RKnee'][:-1])
            angle_right_thigh = cf.getDepthAngle(bones_map_legs[2][4], bone_length_right_thigh)
            if angle_left_thigh > thighAngleThreshold and angle_right_thigh > thighAngleThreshold:
                # if yes skip this frame
                continue
            
            for i in range(len(bones_map_legs)):
            
                if not include_knees_depth and bones_map_legs[i][-1]:
                    continue

                bones[bones_map_legs[i][0]].bone.select = True
                
                bone_length = cf.getDistance_2pts(frames[frame_num][bones_map_legs[i][1]][:-1], frames[frame_num][bones_map_legs[i][2]][:-1])
                Angle = cf.getDepthAngle(bones_map_legs[i][4], bone_length)
                if bones_map_legs[i][5]: 
                    # only subtracting it's half as when the thigh is pushed forward same goes for the shin, it gets nearer to the camera and appears longer in the pose values
                    Angle -= perant_angle/2 
                
                Angle *= (Angle > 0) # if smallar than zero, set to zero
                
                if i == 2: 
                    if frame_num == 36 or frame_num == 37 or frame_num == 38:
                        print(frame_num, Angle)
                        print('bone_length: ', bone_length)
                        print(frames[frame_num][bones_map_legs[i][1]][:-1], frames[frame_num][bones_map_legs[i][2]][:-1])

                if Angle > thighAngleThreshold:
                    if i == 0 or i == 2:
                        leg_moved_forward[bones_map_legs[i][0]][frame_num] = True
                        
                    bpy.context.scene.frame_set(frame_num*(24//fps))
                    bpy.ops.transform.rotate(value=Angle * bones_map_legs[i][3], orient_axis='X', orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', constraint_axis=(True, False, False), mirror=False, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False, release_confirm=True)
                    bpy.ops.anim.keyframe_insert_menu(type='Rotation')
                    
                perant_angle = Angle
            
                bones[bones_map_legs[i][0]].bone.select = False
        ###################################################################  
        
        
        ###################################################################
        ####### XZ plane Thighs Animation #################################
        ###################################################################
        bones_map_thighs = [['ThighLeft', 'LHip', 'LKnee'],
                            ['ThighRight', 'RHip', 'RKnee']]
        thighYAngleThreshold = math.radians(5)
        
        for x1,x2,x3 in bones_map_thighs:
            bones[x1].bone.select = True  
            for frame_num in range(len(frames)-1):
                
                if leg_moved_forward[x1][frame_num]:
                    continue

                bpy.context.scene.frame_set(frame_num*(24//fps))
                
                angle_diff = cf.getAngle_2pts(frames[frame_num][x2][:-1], frames[frame_num][x3][:-1]) + np.deg2rad(90)
                if abs(angle_diff) > thighYAngleThreshold:
                    bpy.ops.transform.rotate(value=angle_diff, orient_axis='Y', orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', constraint_axis=(False, True, False), mirror=False, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False, release_confirm=True)

                angle_left = cf.getAngle_2pts(list(bones['ThighLeft'].head)[:-1], list(bones['ThighLeft'].tail)[:-1])
                angle_right = cf.getAngle_2pts(list(bones['ThighRight'].head)[:-1], list(bones['ThighRight'].tail)[:-1])

                if np.rad2deg(angle_left - angle_right) < -2:
                    diff = (angle_left - angle_right) - np.deg2rad(-2)
                    diff = diff * math.copysign(1,angle_diff)
                    bpy.ops.transform.rotate(value=diff, orient_axis='Y', orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', constraint_axis=(False, True, False), mirror=False, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False, release_confirm=True)

                bpy.ops.anim.keyframe_insert_menu(type='Rotation')
            bones[x1].bone.select = False
        ###################################################################
        

        
        ###################################################################
        ####### Head Rotations ############################################
        ###################################################################
        xAxis_rotation = list(np.zeros(len(frames)))

        bones['SpinalCordB4'].bone.select = True
        
        for frame_num, frame in enumerate(frames):
            
            bpy.context.scene.frame_set(frame_num*(24//fps))

            # Y-axis rotation
            angle_diff = cf.getAngle_2pts(frame['REar'][:-1], frame['LEar'][:-1])
            if abs(angle_diff) > math.radians(5) and frame['REar'][-1] != 0 and frame['LEar'][-1] != 0:
                bpy.ops.transform.rotate(value=angle_diff, orient_axis='Y', orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', constraint_axis=(False, True, False), mirror=False, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False, release_confirm=True)

            # Z-axis rotation 
            if abs(angle_diff) < math.radians(15) or frame['REar'][-1] == 0 or frame['LEar'][-1] == 0:
                angle_diff2 = -cf.getAngle_2pts(frame['Nose'][:-1], frame['Neck'][:-1]) + math.radians(90)
                angle_diff2 *= 2
                bpy.ops.transform.rotate(value=angle_diff2, orient_axis='Z', orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', constraint_axis=(False, False, True), mirror=False, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False, release_confirm=True)

            # X-axis rotation (pre rotation)
            if abs(angle_diff) < math.radians(5) and abs(angle_diff2) < math.radians(5):
                xAxis_rotation[frame_num] = cf.getDistance_2pts(frame['Nose'][:-1], frame['Neck'][:-1])

            bpy.ops.anim.keyframe_insert_menu(type='Rotation')
            
        bones['SpinalCordB4'].bone.select = False

        # X-axis rotation
        xAxis_rotation.sort(reverse=True)
        xAxis_rotation_max_length = sum(xAxis_rotation[: len(frames)//2]) / (len(frames)//2)
        
        bones['SpinalCordB4'].bone.select = True 
        for frame_num in range(len(frames)):
            bpy.context.scene.frame_set(frame_num*(24//fps))

            if xAxis_rotation[frame_num] != 0:
                # negative the angle to tilt the head forward
                angle_x = -cf.getDepthAngle(xAxis_rotation_max_length, xAxis_rotation[frame_num])
                if abs(angle_x) > math.radians(20):
                    bpy.ops.transform.rotate(value=angle_x, orient_axis='X', orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', constraint_axis=(True, False, False), mirror=False, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False, release_confirm=True)
            
            bpy.ops.anim.keyframe_insert_menu(type='Rotation')
            
        bones['SpinalCordB4'].bone.select = False
        ###################################################################
                
                
        
        ###################################################################
        ####### arms (to front& back) Animation ###########################
        ###################################################################
        shoulderAngleThreshold = math.radians(30)
        
        # bones_map_X = [bone in armature, point 1 in pose, point 2 in pose, rotation direction, max length, is child flag]
        '''bones_map_arms = [['ShoulderLeft', 'LShoulder', 'LElbow', 1, 0, False], 
                        #['HandLeft', 'LElbow', 'LWrist', 1, 0, True],
                        ['ShoulderRight', 'RShoulder', 'RElbow', 1, 0, False]]
                        #['HandRight', 'RElbow', 'RWrist', 1, 0, True]]
        
        for i in range(len(bones_map_arms)):
            bone_lengths = []
            for frame_num in range(len(frames)):
                bone_length = cf.getDistance_2pts(frames[frame_num][bones_map_arms[i][1]][:-1], frames[frame_num][bones_map_arms[i][2]][:-1])
                bone_lengths.append(bone_length)
                
            bone_lengths.sort(reverse=True)
            bones_map_arms[i][4] = sum(bone_lengths[: len(frames)//2]) / (len(frames)//2)

        perant_angle = 0
        for frame_num in range(1,len(frames)):

            for i in range(len(bones_map_arms)):
                bone_length = cf.getDistance_2pts(frames[frame_num][bones_map_arms[i][1]][:-1], frames[frame_num][bones_map_arms[i][2]][:-1])
                Angle = cf.getDepthAngle(bones_map_arms[i][4], bone_length)
                if bones_map_arms[i][5]: Angle -= perant_angle/2 # only subtracting it's half as when the thigh is pushed forward same goes for the shin, it gets nearer to the camera and appears longer in the pose values
                #print(bones_map_arms[i][0], ': ', Angle)
                
                Angle = 0 if Angle < 0 else Angle
                
                # and cf.getAngle_2pts(list(bones[bones_map_arms[i][0]].head)[:-1], list(bones[bones_map_arms[i][0]].tail)[:-1], degree = True) > 
                if Angle > shoulderAngleThreshold: 
                    bones[bones_map_arms[i][0]].bone.select = True
                    bpy.context.scene.frame_set(frame_num*(24//fps)) 
                    bpy.ops.transform.rotate(value = Angle * bones_map_arms[i][3], orient_axis='Z', orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', constraint_axis=(False, False, True), mirror=False, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False, release_confirm=True)
                    bpy.ops.anim.keyframe_insert_menu(type='Rotation')
                    bones[bones_map_arms[i][0]].bone.select = False
                    
                perant_angle = Angle
        ###################################################################'''

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
        bpy.ops.object.select_all(action='DESELECT') # Deselect all objects
        bpy.ops.import_scene.obj(filepath = (cf.MAIN_DIR) + "\\1_human.obj")
        bpy.context.view_layer.objects.active = bpy.context.selected_objects[0]
        
    def add_armature(context,self):
        model = bpy.context.active_object #get the armature object
        bpy.ops.object.add(type = "ARMATURE")
        
        obArm = bpy.context.active_object #get the armature object
        obArm.location = model.location
        obArm.rotation_euler = model.rotation_euler
        bpy.ops.object.mode_set(mode='EDIT', toggle=False)
        ebs = obArm.data.edit_bones

        rigInfo = self.readRigInfo(cf.MAIN_DIR + "\\landmarks_v1.json")
    
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
        
        obj.rotation_euler.z += np.deg2rad(180)

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
    bpy.utils.register_class(animate)
    bpy.utils.register_class(test)
 
def unregister() :
    bpy.utils.unregister_class(TestPanel)
    bpy.utils.unregister_class(addReggedModel)
    bpy.utils.unregister_class(deleteModel)
    bpy.utils.unregister_class(animate)
    bpy.utils.unregister_class(test)
    
if __name__ == "__main__":
    register()
