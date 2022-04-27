import json
import math

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
        Dict[Map[i]] = [arr[j], arr[j+1], arr[j+2]]
        
    return Dict

def getAngle_2pts(p1, p2, degree=False):
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    angle = math.atan2(dy, dx)
    
    if degree:
        angle = math.degrees(angle)
        
    return angle