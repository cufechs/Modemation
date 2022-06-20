#include <iostream>
#include <string> 
#include "BuildSSM.h"


int main(int argc, char *argv[]) {

    BuildSSM ssm;
    //ssm.loadPCAModel("/Users/abdelrahmanabdelghany/Documents/college/semester10/GP/Human3D/tests/pcaModel_male_630_smplx_v2_T.h5",
    ssm.loadPCAModel("/Users/abdelrahmanabdelghany/Documents/college/semester10/GP/Human3D/models/pcaModel_female.h5",
        "/Users/abdelrahmanabdelghany/Documents/college/semester10/GP/Human3D/tests/referenceObj.obj");

    Eigen::VectorXf coefficients(7);
    coefficients.setZero();

    for (int i = 0; i < 7; i++) 
        coefficients[i] = std::stof(argv[i+1]);

    Mesh sampledMesh = ssm.instance(coefficients); 
    std::cout << "sampled mesh instanced\n";

    sampledMesh.scale(1000.0);
    sampledMesh.computeNormals();
    ObjLoader::saveObj("/Users/abdelrahmanabdelghany/Documents/college/semester10/GP/Human3D/tests/meshTestSampledFromSavedModel_female_v1.obj",
     sampledMesh.points, sampledMesh.pointIds, sampledMesh.triangleCells,
     sampledMesh.normals, sampledMesh.textureCoords);

    ssm.readIdsIndicesLandmarks("/Users/abdelrahmanabdelghany/Documents/college/semester10/GP/Human3D/tests/ids_index.json");
    ssm.saveLandmarks("/Users/abdelrahmanabdelghany/Documents/college/semester10/GP/Human3D/tests/meshTestSampledFromSavedModelLandmarks_female_v1.json",sampledMesh);
    

    std::cout << "sampling pca model done.\n";
    return 0;
}