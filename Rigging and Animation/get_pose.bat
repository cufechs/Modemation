#!/bin/bash

py preprocessing/clear_dir.py


:: Segmenting input image
py preprocessing/get_image.py 

cd HumanSeg
py bg_replace.py --config export_model/deeplabv3p_resnet50_os8_humanseg_512x512_100k_with_softmax/deploy.yaml --img_path data/human.jpg
cd output
move human.png ..
cd ..
move human.png ..
cd ..
move human.png frames
cd frames
move human.png initial
cd .. 

py preprocessing/crop_image.py 


::::::::::::::::::::::::::::::::::::::::


:: Getting frames
py preprocessing/get_frames.py -mfps 1 -rf 4

move frames openpose

cd openpose

bin\\OpenPoseDemo.exe --image_dir frames/ --write_json frames/pose/
bin\\OpenPoseDemo.exe --image_dir frames/initial/ --write_json frames/initial/

move frames ..

::::::::::::::::::::::::::::::::::::::::

