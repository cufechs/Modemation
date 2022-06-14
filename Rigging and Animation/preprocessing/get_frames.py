from os import listdir
import cv2
from math import floor
from argparse import ArgumentParser



ap = ArgumentParser()
ap.add_argument("-mfps", "-min_frame_sec", default=4, type=int, help="frames to extract per second")
ap.add_argument("-rf", "-resize_factor", default=1, type=int, help="resizeing factor, 1 -> 1280x720 & 2 -> 640x360")
args = vars(ap.parse_args())


if __name__ == '__main__' :

    # get video file name
    list_mp4s = [f for f in sorted(listdir('inputs/video/')) if ((str(f))[-3:] == "mp4" or (str(f))[-3:] == "avi" or (str(f))[-3:] == "mkv")]
    vidcap = cv2.VideoCapture('inputs/video/' + list_mp4s[0])

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
    hight, width = image.shape[:2]
    frames_count = 0
    gap = 0
    while success:    
        if gap == 0:
            frames_count += 1
            resized_image = cv2.resize(image, (width//resize_factor, hight//resize_factor), interpolation = cv2.INTER_NEAREST)
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
   