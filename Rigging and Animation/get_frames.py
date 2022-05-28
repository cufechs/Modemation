import os
import cv2
from math import floor
import argparse


ap = argparse.ArgumentParser()
ap.add_argument("-mfps", "-min_frame_sec", default=4, type=int, help="frames to extract per second")
ap.add_argument("-rf", "-resize_factor", default=1, type=float, help="resizeing factor, 1 -> 1280x720 & 2 -> 640x360")
args = vars(ap.parse_args())


if __name__ == '__main__' :

    # create 'frames' dir if not there, and if there flush it
    try: 
        os.mkdir('frames') 
    except OSError as error:
        # flush dir 'frames'
        for f in os.listdir('frames'):
            os.remove(os.path.join('frames', f))

    # get video file name
    list_mp4s = [f for f in sorted(os.listdir('input_video/')) if ((str(f))[-3:] == "mp4" or (str(f))[-3:] == "mp4")]
    vidcap = cv2.VideoCapture('input_video/' + list_mp4s[0])

    min_fps = args['mfps']
    resize_factor = args['rf']
    
    fps = vidcap.get(cv2.CAP_PROP_FPS)
    frames_count = int(vidcap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = frames_count/fps

    frames = floor(duration*min_fps)
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
            resized_image = cv2.resize(image, (1280//resize_factor, 720//resize_factor), interpolation = cv2.INTER_NEAREST)
            cv2.imwrite("frames/frame%d.jpg" % frames_count, resized_image)     # save frame as JPG file      
            success, image = vidcap.read()
            gap += frames_gap-1
            continue
        
        success, _ = vidcap.read()
        gap -= 1
    
    #saving my_fps in my_fps.txt
    f = open("frames/pose/my_fps.txt", "a")
    f.write(str(my_fps))
    f.close()
   