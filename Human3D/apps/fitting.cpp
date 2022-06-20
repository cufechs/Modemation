#include <iostream>
#include "MetropolisHastings.h"

/**
 * @brief fits the pca shape model built on input body proportions of 2D human image
 * 
 * @usage ./fitting ../models/pcaModel_male.csv ../models/meanMesh.csv ../data/referenceObj.obj ../data/ids_index_v2.json ../data/inputParamsjson ../output/finalMesh7.obj ../output/finalLms7.json
 * 
 * @param argv[1] - pca shape model csv file path
 * @param argv[2] - mean mesh csv file path
 * @param argv[3] - reference mesh obj file path
 * @param argv[4] - ids indices json file path
 * @param argv[5] - input json file with proportions
 * @param argv[6] - output fitted mesh obj file path
 * @param argv[7] - output landmarks json file path
 * 
 */
int main(int argc, char *argv[]) {

    std::cout << "[Fitting]::starting fitting...\n";

    BuildSSM ssm;

    ssm.loadPCAModel_CSV(std::string(argv[1]), std::string(argv[2]),
        std::string(argv[3]));
    std::cout << "[Fitting]::loaded model successfully\n";

    ssm.readIdsIndicesLandmarks(std::string(argv[4]));
    std::cout << "[Fitting]::reading ids_index json successfully\n";

    Eigen::VectorXf coefficients(7);
    coefficients.setZero();

    float sdevProposal = 0.05f;
    float sdevLikelihood = 0.01f;
    float sdevPrior = 1.0f;
    int numIterations = 7000;

    MetropolisHastings metropolis(&ssm, std::string(argv[5]), coefficients, sdevProposal, sdevLikelihood, sdevPrior);
    Model fittedModel = metropolis.run(numIterations);
    std::cout << "[Fitting]::fitting model done\n";

    fittedModel.saveMesh(std::string(argv[6]));
    std::cout << "[Fitting]::saved fitted mesh\n";

    fittedModel.saveLandmarks(ssm.getIdsIndicesJson(), std::string(argv[7]));
    std::cout << "[Fitting]::saved landmarks\n";

    std::cout << "[Fitting]::done fitting\n";
    return 0;
}