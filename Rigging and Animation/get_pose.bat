#!/bin/bash

py get_frames.py -mfps 5 -rf 4

move frames openpose

cd openpose

bin\\OpenPoseDemo.exe --image_dir frames/ --write_json frames/pose/

move frames ..

