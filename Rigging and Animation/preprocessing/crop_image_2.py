import cv2
import json
import numpy as np
from os import listdir
from skimage.color import rgba2rgb


def parse_face_80(Dir = 'frames/initial/human_keypoints.json'):
    f = open(Dir)
    data = json.load(f)
    arr = data['people'][0]['face_keypoints_2d']

    Dict = {}
    for i in range(70):
        j=i*3
        Dict[i] = [arr[j], 1-arr[j+1], arr[j+2]]

    return Dict

if __name__ == '__main__' :

    list_image = [f for f in sorted(listdir('frames/initial/')) if ((str(f))[-3:] == "png" or (str(f))[-3:] == "jpg" or (str(f))[-4:] == "jpeg")]
    path = 'frames/initial/' + list_image[0]
    
    img = cv2.imread(path, cv2.IMREAD_UNCHANGED)

    face_points = parse_face_80()

    mid_face_pts = [27,28,29,30,51,57,62,8]

    mid_x = 0
    for pt in mid_face_pts:
        mid_x += face_points[pt][0]
        
    mid_x = int(mid_x // len(mid_face_pts))
    img_shape = img.shape
    img_2 = None
    if mid_x > img.shape[1] - mid_x:
        img_2 = np.zeros((img_shape[0], img_shape[1] + (mid_x*2 - img_shape[1]), img_shape[2]))
        img_2[:,:img.shape[1],:] = img
    else:
        img_2 = np.zeros((img_shape[0], img_shape[1] + (img_shape[1] - mid_x*2), img_shape[2]))
        img_2[:,-img.shape[1]:,:] = img
    
    cv2.imwrite(path, img_2)    