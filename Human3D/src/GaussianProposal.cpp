#include "GaussianProposal.h"

GaussianProposal::GaussianProposal(float standardDeviation) : ProposalDistribution(standardDeviation) {
    // create a tmp distribution with standardDeviation
    std::normal_distribution<float> distributionTmp{0.0f, 1.0f};//standardDeviation};
    // update the standardDeviation
    distribution.param(distributionTmp.param());
}

GaussianProposal::~GaussianProposal() {

}

Eigen::VectorXf GaussianProposal::propose(Eigen::VectorXf params) {
    Eigen::VectorXf proposedParams(params.size());
    
    for (int i = 0; i < params.size(); i++) {
        float r = distribution(generator);
        //std::cout << "*********************** r = " << r << "\n";
        // if (i >= 3)
        // proposedParams[i] = params[i];// + (standardDeviation/5) *  r;
        // else
        proposedParams[i] = params[i] + standardDeviation *  r;
        if (proposedParams[i] > 1.0) proposedParams[i] = 1.0;
        if (proposedParams[i] < -1.0) proposedParams[i] = -1.0;
        // if (i < 10)
        //     std::cout << "params[i] = " << params[i] << ",   proposedParams[i] = " <<  proposedParams[i] << "\n";
    }

    return proposedParams;
}

float GaussianProposal::evaluateLogTransitionProbability(Eigen::VectorXf fromParams, Eigen::VectorXf toParams) {
    
    float sumLogValues = 0.0;
    //std::cout << "[GaussianProposal::evaluateLogTransitionProbability]::standardDeviation = " << standardDeviation << "\n";
    if (fromParams.size() != toParams.size()) {
        std::cerr << "[ERROR]::fromParams and toParams are not the same size!\n";
        return -1.0;
    }

    float denom = -0.5 * log(2 * M_PI) - log(standardDeviation);
    // x: to
    // mean: from
    for (int i = 0; i < fromParams.size(); i++) {
        sumLogValues += denom - (0.5 * (toParams[i] - fromParams[i]) * (toParams[i] - fromParams[i])) / (standardDeviation * standardDeviation);
    }

    return sumLogValues;
}