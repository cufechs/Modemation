cd ..

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

py preprocessing/crop_image_1.py


:: Getting frames
py preprocessing/get_frames.py -mfps 6 -rf 4
move frames openpose
cd openpose

:: Get video frames pose
::bin\\OpenPoseDemo.exe --image_dir frames/ --write_json frames/pose/

:: Get input image pose
bin\\OpenPoseDemo.exe --image_dir frames/initial/ --face --write_json frames/initial/

move frames ..
cd ..
::::::::::::::::::::::::::::::::::::::::


:: cropping input image and extract proportions 
py preprocessing/crop_image_2.py 
py preprocessing/get_proportions.py -out_dir human_proportions.json -s
::::::::::::::::::::::::::::::::::::::::


:: Model building
move human_proportions.json .. 
cd .. 
move human_proportions.json Human3D
cd Human3D
move human_proportions.json data

.\build\Debug\fitting models/pcaModel_male.csv models/meanMesh.csv data/referenceObj.obj data/ids_index_v2.json data/human_proportions.json model_output/mesh.obj model_output/rigInfo.json

move model_output ..
cd .. 
move model_output RiggingAndAnimation
cd RiggingAndAnimation
::::::::::::::::::::::::::::::::::::::::

