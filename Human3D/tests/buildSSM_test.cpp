#include <iostream>
#include "BuildSSM.h"
//#include <glm/ext.hpp>
#include <glm/gtx/euler_angles.hpp>
#include <glm/gtc/matrix_transform.hpp>
#include <glm/gtx/transform.hpp>

void printVec(glm::vec3 v) {
    std::cout << "vec: (" << v.x << ", " << v.y << ", " << v.z << ")\n";
}



int main(int argc, char *argv[]) {

    std::cout << "[BuildSSM] included successfully\n";

    std::string male_dir = "/Users/abdelrahmanabdelghany/Downloads/data11_noexp";
    //std::string male_dir = "/Users/abdelrahmanabdelghany/Documents/college/semester10/GP/Human3D/data/male_T_80_noexp";
    BuildSSM ssm(male_dir);
    std::size_t p = male_dir.find_last_of('/');
    std::cout << "p: " << p << "\n";
    
    ssm.createModelsFromFiles();
    std::cout << "[BuildSSM] created models from files\n";
ssm.computeGPA();
    ssm.createDeformationFields();

    //ssm.computeGPA();

    // ssm.models[8].mesh.computeNormals();
    // // test saving a mesh after computing generalized procrustes alignment
    // ObjLoader::saveObj("/Users/abdelrahmanabdelghany/Documents/college/semester10/GP/Human3D/tests/meshTest1_T.obj",
    //  ssm.models[8].mesh.points, ssm.models[8].mesh.pointIds, ssm.models[8].mesh.triangleCells,
    //  ssm.models[8].mesh.normals, ssm.models[8].mesh.textureCoords);
    

    ssm.createPCA();

    Eigen::VectorXf coefficients(10);
    coefficients.setZero();
    coefficients[atoi(argv[1])] = std::stof(argv[2]);
    std::cout << "argv[1]: " << std::stof(argv[1]) << "\n";
    Mesh sampledMesh =  ssm.sampleSSM(coefficients); //ssm.createMeanModel().mesh ;//
    sampledMesh.computeNormals();


    sampledMesh.scale(1000.0f);
    ObjLoader::saveObj("/Users/abdelrahmanabdelghany/Documents/college/semester10/GP/Human3D/tests/meshTestSampled300_T.obj",
     sampledMesh.points, sampledMesh.pointIds, sampledMesh.triangleCells,
     sampledMesh.normals, sampledMesh.textureCoords);

    ssm.readIdsIndicesLandmarks("/Users/abdelrahmanabdelghany/Documents/college/semester10/GP/Human3D/tests/ids_index.json");
    ssm.saveLandmarks("/Users/abdelrahmanabdelghany/Documents/college/semester10/GP/Human3D/tests/meshTestSampledLandmarks300_T.json",sampledMesh);
    std::cout << "going to save pca model\n";
    ssm.savePCAModel("/Users/abdelrahmanabdelghany/Documents/college/semester10/GP/Human3D/tests/pcaModel_male_300_T.h5");

    return 0;
}