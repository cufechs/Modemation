#include <iostream>
#include <string> 
#include "BuildSSM.h"


int main(int argc, char *argv[]) {

    BuildSSM ssm;
    ssm.loadPCAModelSmpl("/Users/abdelrahmanabdelghany/Documents/college/semester10/GP/Human3D/tests/pcaModel_male_630_smpl_T.h5",
        "/Users/abdelrahmanabdelghany/Documents/college/semester10/GP/Human3D/data/smpl/smpl_uv.obj");

    Eigen::VectorXf coefficients(10);
    coefficients.setZero();
    //coefficients[atoi(argv[1])] = std::stof(argv[2]);
    //std::cout << "argv[1]: " << std::stof(argv[1]) << "\n";
    //coefficients[0] = std::stof(argv[1]);
    //coefficients[1] = std::stof(argv[2]);

    for (int i = 0; i < 10; i++) 
        coefficients[i] = std::stof(argv[i+1]);

    Mesh sampledMesh = ssm.instance(coefficients); 
    std::cout << "sampled mesh instanced\n";

    sampledMesh.scale(1000.0);
    ObjLoader::saveObj("/Users/abdelrahmanabdelghany/Documents/college/semester10/GP/Human3D/tests/meshTestSampledFromSavedModel_630.obj",
     sampledMesh.points, sampledMesh.pointIds, sampledMesh.triangleCells,
     sampledMesh.normals, sampledMesh.textureCoords);

    ssm.readIdsIndicesLandmarks("/Users/abdelrahmanabdelghany/Documents/college/semester10/GP/Human3D/data/smpl/ids_index_smpl.json");
    ssm.saveLandmarks("/Users/abdelrahmanabdelghany/Documents/college/semester10/GP/Human3D/tests/meshTestSampledFromSavedModelLandmarks_630.json",sampledMesh);
    

    std::cout << "sampling pca model done.\n";
    return 0;
}