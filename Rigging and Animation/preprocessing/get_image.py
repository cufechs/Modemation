from os import listdir
import shutil
import cv2
from skimage.color import rgba2rgb


if __name__ == '__main__' :

    #move image pose
    list_image = [f for f in sorted(listdir('inputs/image/')) if ((str(f))[-3:] == "png" or (str(f))[-3:] == "jpg" or (str(f))[-4:] == "jpeg")]
    image_extention = list_image[0].split('.')[-1]
    
    im1 = cv2.imread('inputs/image/' + list_image[0])
    pth = 'HumanSeg/data/human.jpg'
    if im1.shape[-1] == 4:
        im1 = rgba2rgb(im1)
    cv2.imwrite(pth, im1)    
   