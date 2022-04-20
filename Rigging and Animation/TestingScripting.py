import bpy
import json
import math
import mathutils
import numpy as np
from mathutils import Matrix

class TestPanel(bpy.types.Panel):
    bl_label = "Test Panel"
    bl_idname = "PT_TestPanel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "NewTab"

    def draw(self, context):
       self.layout.operator("mesh.add_cube_sample", icon='MESH_CUBE', text="Import Model")
       self.layout.operator("mesh.add_armature", icon='MESH_CUBE', text="Add Armature")            
       self.layout.operator("mesh.apply_ik", icon='GIZMO', text="Apply IK")  

class applyIK(bpy.types.Operator):
    bl_idname = 'mesh.apply_ik'
    bl_label = 'Apply IK'
    bl_options = {"REGISTER", "UNDO"}
 
    def normalize(self, vect):
        val = np.array(vect)
        return val / np.linalg.norm(val)
 
    def execute(self, context):
        
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
                
                bpy.ops.object.mode_set(mode='EDIT', toggle=False)
                selected_ob.data.edit_bones["FistLeft"].parent = None
                bpy.ops.object.mode_set(mode='POSE', toggle=False)

                v = fistLeft.head - handLeft.head
                bv = handLeft.tail - handLeft.head

                rd = bv.rotation_difference(v)

                M = (
                    Matrix.Translation(handLeft.head) @
                    rd.to_matrix().to_4x4() @
                    Matrix.Translation(-handLeft.head)
                )
                handLeft.matrix = M @ handLeft.matrix
                
                bpy.ops.object.mode_set(mode='EDIT', toggle=False)
                selected_ob.data.edit_bones["FistLeft"].parent = selected_ob.data.edit_bones["HandLeft"]
                bpy.ops.object.mode_set(mode='POSE', toggle=False)
                
                #fistLeft.parent = handLeft

                #shoulderLeft.tail = shoulderLeft.head + mathutils.Vector(direction * shoulderLeft.length)
                #handLeft.head = shoulderLeft.tail
                #handLeft.tail = handLeft.head + mathutils.Vector(direction * handLeft.length)
            
        return {"FINISHED"}
        
class addCubeSample(bpy.types.Operator):
    bl_idname = 'mesh.add_cube_sample'
    bl_label = 'Add Cube'
    bl_options = {"REGISTER", "UNDO"}
 
    def execute(self, context):
        bpy.ops.import_mesh.stl(filepath = "C:\\Users\\ossya\\Documents\\BlenderScripting\\Rigging and Animation\\Mesh.stl")
        return {"FINISHED"}
    
class addArmature(bpy.types.Operator):
    bl_idname = 'mesh.add_armature'
    bl_label = 'Add Armature'
    bl_options = {"REGISTER", "UNDO"}
    
    def readRigInfo(self, fileName):
        with open(fileName, "r") as read_file:
            rigInfo = json.load(read_file)
        
        return rigInfo
 
    def execute(self, context):
        model = bpy.context.active_object #get the armature object
        print(model.name)
        print(model.location)
        bpy.ops.object.add(type = "ARMATURE")
        
        obArm = bpy.context.active_object #get the armature object
        obArm.location = model.location
        obArm.rotation_euler = model.rotation_euler
        bpy.ops.object.mode_set(mode='EDIT', toggle=False)
        ebs = obArm.data.edit_bones

        rigInfo = self.readRigInfo("C:\\Users\\ossya\\Documents\\BlenderScripting\\Rigging and Animation\\RigInfo.json")
        
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
        
        return {"FINISHED"}
    
def fabrik_ik(context):
    print("Hello World")   
    
bpy.app.handlers.frame_change_pre.append(fabrik_ik) 
 
def register() :
    bpy.utils.register_class(TestPanel)
    bpy.utils.register_class(addCubeSample)
    bpy.utils.register_class(addArmature)
    bpy.utils.register_class(applyIK)
 
def unregister() :
    bpy.utils.unregister_class(TestPanel)
    bpy.utils.unregister_class(addCubeSample)
    bpy.utils.unregister_class(addArmature)
    bpy.utils.unregister_class(applyIK)
    
if __name__ == "__main__":
    register()