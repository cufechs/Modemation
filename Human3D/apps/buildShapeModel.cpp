#include <iostream>
#include "BuildSSM.h"
#include <glm/gtx/euler_angles.hpp>
#include <glm/gtc/matrix_transform.hpp>
#include <glm/gtx/transform.hpp>

/**
 * @brief create pca shape model from directory and reference mesh and save the model and mean mesh in csv format
 * 
 * @param argv[1] - meshes directory path to build the model on 
 * @param argv[2] - reference mesh obj file path
 * @param argv[3] - output pca model csv file path to be saved at
 * @param argv[4] - output mean mesh csv file to be saved at
 * 
 */
int main(int argc, char *argv[]) {


    std::cout << "[buildShapeModel]::start building shape model...\n";
    
    // read input pathes from command line (first and second arguments)
    std::string meshes_dir = std::string(argv[1]);
    std::string reference_obj = std::string(argv[2]);

    // create statistical shape model
    BuildSSM ssm(meshes_dir, reference_obj);

    // load model files
    ssm.createModelsSmpl();
    std::cout << "[buildShapeModel]::loaded model fils\n";
    
    ssm.computeGPA();
    std::cout << "[buildShapeModel]::computed Generalized Procrustes Alignment\n";

    ssm.createDeformationFields();
    std::cout << "[buildShapeModel]::created deformation fields\n";
 
    ssm.createPCA();
    std::cout << "[buildShapeModel]::created pca shape model\n";

    //ssm.savePCAModel(std::string(argv[3]));
    ssm.savePCAModel_CSV(std::string(argv[3]), std::string(argv[4]));
    std::cout << "[buildShapeModel]::saved pca shape model\n";

    return 0;
}