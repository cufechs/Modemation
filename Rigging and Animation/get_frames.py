import os
import cv2
from math import floor

if __name__ == '__main__' :

    # create 'frames' dir if not there, and if there flush it
    try: 
        os.mkdir('frames') 
    except OSError as error:
        # flush dir 'frames'
        for f in os.listdir('frames'):
            os.remove(os.path.join('frames', f))

    list_mp4s = [f for f in sorted(os.listdir('input_video/')) if ((str(f))[-3:] == "mp4" or (str(f))[-3:] == "mp4")]
    vidcap = cv2.VideoCapture('input_video/' + list_mp4s[0])


    fps = vidcap.get(cv2.CAP_PROP_FPS)
    frames_count = int(vidcap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = frames_count/fps

    frames = floor(duration*4)
    frames_gap = frames_count // frames
    frames_taken = frames_count // frames_gap
    frames_dropped = (frames_count-1) % frames_gap
    my_fps = frames_taken / (duration - (frames_dropped*(1/fps)))
    
    success,image = vidcap.read()
    frames_count = 0
    gap = 0
    while success:    
        if gap == 0:
            frames_count += 1
            cv2.imwrite("frames/frame%d.jpg" % frames_count, image)     # save frame as JPG file      
            success, image = vidcap.read()
            gap += frames_gap-1
            continue
        
        success, _ = vidcap.read()
        gap -= 1
    
    #saving my_fps in my_fps.txt
    f = open("frames/my_fps.txt", "a")
    f.write(str(my_fps))
    f.close()
   