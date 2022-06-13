from os import listdir
import shutil
import cv2
from skimage.color import rgba2rgb


if __name__ == '__main__' :

    list_image = [f for f in sorted(listdir('frames/initial/')) if ((str(f))[-3:] == "png" or (str(f))[-3:] == "jpg" or (str(f))[-4:] == "jpeg")]
    path = 'frames/initial/' + list_image[0]
    
    img = cv2.imread(path, cv2.IMREAD_UNCHANGED)
    
    img[:,:,-1] = (img[:,:,-1] >= 150) * 255
    

    im = img[:,:,-1]
    Y,X = im.shape
    
    pad = 10
    
    x1,y1,x2,y2 = 0,0,X-1,Y-1

    for x in range(pad, X):
        if sum(im[:,x]) > 1:
            x1 = x
            break
    
    for y in range(pad, Y):
        if sum(im[y,:]) > 1:
            y1 = y
            break
            
    for x in range(X-1-pad, 0, -1):
        if sum(im[:,x]) > 1:
            x2 = x
            break
            
    for y in range(Y-1-pad, 0, -1):
        if sum(im[y,:]) > 1:
            y2 = y
            break 
            
    cv2.imwrite(path, img[y1:y2+1, x1:x2+1, :])    