#!/bin/bash

py preprocessing/get_frames.py -mfps 5 -rf 4

move frames openpose

cd openpose

bin\\OpenPoseDemo.exe --image_dir frames/ --write_json frames/pose/
bin\\OpenPoseDemo.exe --image_dir frames/initial/ --write_json frames/initial/

move frames ..

