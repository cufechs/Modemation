from os import listdir
import cv2
import json
from argparse import ArgumentParser

ap = ArgumentParser()
ap.add_argument('-s', '--show', action='store_true')
args = ap.parse_args()


if __name__ == '__main__' :

    list_image = [f for f in sorted(listdir('frames/initial/')) if ((str(f))[-3:] == "png" or (str(f))[-3:] == "jpg" or (str(f))[-4:] == "jpeg")]
    path = 'frames/initial/' + list_image[0]
    
    img = cv2.imread(path, cv2.IMREAD_UNCHANGED)

    h, w = img.shape[:2]
    
    dic = {}
    dic['height'] = img.shape[0]
    dic['arm_span'] = img.shape[1]
    dic['belly'] = int(sum(img[2*h//5, :, -1])//255)
    dic['ankle'] = int(sum(img[9*h//10, :, -1])//(255*2))
    dic['knee'] = int(sum(img[7*h//10, :, -1])//(255*2))
    dic['thigh'] = int(sum(img[11*h//20, :, -1])//(255*2))
    
    
    mini, neck = w, 0
    for y in range(1*h//20, h//5):
        wid = sum(img[y, :, -1])//255
        if mini > wid:
            mini, neck = wid, y
    dic['neck'] = int(sum(img[neck, :, -1])//255)
    dic['head_length'] = neck
    
    maxi, face_width = 0, 0
    for y in range(neck):
        wid = sum(img[y, :, -1])//255
        if maxi < wid:
            maxi, face_width = wid, y
    dic['head_width'] = int(sum(img[face_width, :, -1])//255)
    
    maxi, arm_span_h = 0, 0
    for y in range(neck, 1*h//3):
        wid = sum(img[y, :, -1])//255
        if maxi < wid:
            maxi, arm_span_h = wid, y
            
    for y in range(arm_span_h, (arm_span_h+2*h//5)//2):
        wid = sum(img[y, :, -1])//255
        if maxi < wid:
            maxi, arm_span_h = wid, y       

    expected_chest_h = (arm_span_h*3+(2*h//5))//4
    while sum(img[expected_chest_h, :, -1])//255 > (sum(img[expected_chest_h + int(h*0.01), :, -1])//255)*1.05:
        expected_chest_h += int(h*0.01)
    dic['chest_width'] = int(sum(img[expected_chest_h, :, -1])//255)
    
    legs_start = (2*h//5 + 11*h//20)//2
    dic['leg_length'] = int(h - (2*h//5 + 11*h//20)//2)
    
    with open('frames/initial/human_proportions.json', 'w') as outfile:
        outfile.write(json.dumps(dic))

    if args.show:
        path = 'test/proportions.png'
        mask = img[:,:,-1].copy()
    
        cv2.line(img, (0, 2*h//5), (w, 2*h//5), (0,0,255,255), 2) # belly
        cv2.line(img, (0, 9*h//10), (w, 9*h//10), (0,0,255,255), 2) # ankle
        cv2.line(img, (0, 7*h//10), (w, 7*h//10), (0,0,255,255), 2) # knee
        cv2.line(img, (0, 11*h//20), (w, 11*h//20), (0,0,255,255), 2) # thigh
        cv2.line(img, (0, neck), (w, neck), (0,0,255,255), 2) # neck
        cv2.line(img, (w//2, 0), (w//2, neck), (0,255,0,255), 2) # face length
        cv2.line(img, (0, face_width), (w, face_width), (0,0,255,255), 2) # face width
        cv2.line(img, (0, expected_chest_h), (w, expected_chest_h), (0,0,255,255), 2) # chest width
        
        cv2.line(img, (w//2 + w//20, legs_start), (w//2 + w//20, h), (0,255,0,255), 2) # left leg length
        cv2.line(img, (w//2 - w//20, legs_start), (w//2 - w//20, h), (0,255,0,255), 2) # right leg length
        
        img[:,:,-1] *= (mask//255)
        cv2.imwrite(path, img)    