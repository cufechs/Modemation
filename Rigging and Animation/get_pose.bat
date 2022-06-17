
cd "S:\Semester 10 (Spring-2022)\Graduation project\Modemation\Rigging and Animation"


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
::::::::::::::::::::::::::::::::::::::::



:: Get input image pose
py preprocessing/crop_image_1.py
move frames openpose
cd openpose
bin\\OpenPoseDemo.exe --image_dir frames/initial/ --face --write_json frames/initial/
move frames ..
cd ..
::::::::::::::::::::::::::::::::::::::::



:: Model building


::::::::::::::::::::::::::::::::::::::::



:: Getting frames
::py preprocessing/get_frames.py -mfps 1 -rf 4

::move frames openpose
::cd openpose

::bin\\OpenPoseDemo.exe --image_dir frames/ --write_json frames/pose/
::move frames ..
::cd ..

::::::::::::::::::::::::::::::::::::::::


:: Postprocessing on inpit image to fit as a texture
py preprocessing/crop_image_2.py 
py preprocessing/get_proportions.py -s
::::::::::::::::::::::::::::::::::::::::
