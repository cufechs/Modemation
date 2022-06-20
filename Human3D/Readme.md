# Human 3D

### Installation

make sure to have [Eigen 3.3](https://eigen.tuxfamily.org/index.php?title=Main_Page) installed on your system 

```{sh}
git clone https://github.com/amamdouhmahfouz/Human3D.git
cd Human3D
cmake -S. -Bbuild
cmake --build build
```

### Download Model

male model + mean mesh: https://drive.google.com/file/d/1qbm_t9WqNWRJKyZP17T1H536AZDGmSHo/view?usp=sharing 
> put the downloaded model and the mean mesh in the models folder

### Usage
***make sure you are in the build directory***

Fit shape model on input json with proportions:
```{sh}
./build/fitting models/pcaModel_male.csv models/meanMesh.csv data/referenceObj.obj data/ids_index_v2.json data/inputParams.json output/finalMesh7.obj output/finalLms7.json
```

Build your own shape model from a directory:
```{sh}
./build/buildShapeModel path_to_meshes_dir path_to_meanMesh data/referenceObj.obj output_path_for_csv_model output_path_for_csv_meanMesh
```

### Datasets
You can use your own acquired datasets or one of the datasets we have used 

1. [SPRING](https://graphics.soe.ucsc.edu/data/BodyModels/index.html)
2. Generate your own from [SMPLX](https://github.com/vchoutas/smplx) (see the examples/demo.py in their repo)