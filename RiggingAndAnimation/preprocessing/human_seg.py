import cv2
import numpy as np
from os import listdir
from skimage.feature import canny
from skimage.color import rgb2gray, rgba2rgb
from skimage.morphology import binary_closing


def segment_human(image):
    mask1 = np.zeros(image[:,:,-1].shape)
    mask3 = np.zeros(image[:,:,-1].shape)
    img = image.copy()
    gray = np.uint8(rgb2gray(rgba2rgb(image.copy()))*255)
    edged = np.uint8(canny(gray,sigma=1))
    cnts = cv2.findContours(edged, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts)==2 else cnts[1]
    
    if len(cnts) > 0:
        cnts = sorted(cnts, key=cv2.contourArea, reverse=True)
        cv2.drawContours(mask1, cnts, -1, (1), 3)
        
    mask2 = binary_closing(mask1, np.ones((10, 10), np.uint8))
    
    edged = np.uint8(canny(mask2,sigma=0))
    cnts = cv2.findContours(edged, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts)==2 else cnts[1]
    
    if len(cnts) > 0:
        cnts = sorted(cnts, key=cv2.contourArea, reverse=True)
        cv2.drawContours(mask3, cnts, 0, (1), -1)
        
    img[:,:,-1] = img[:,:,-1] * mask3
    return img


if __name__ == '__main__' :

    #move image pose
    list_image = [f for f in sorted(listdir('inputs/')) if ((str(f))[-3:] == "png" or (str(f))[-3:] == "jpg" or (str(f))[-4:] == "jpeg")]
    image_split = list_image[0].split('.')
    
    img = cv2.imread('inputs/' + list_image[0], cv2.IMREAD_UNCHANGED)
    
    img = segment_human(img)
    
    
    pth = 'HumanSeg/data/human.jpg'
    cv2.imwrite('inputs/' + image_split[0] + "_seg." + image_split[-1], img)    
   