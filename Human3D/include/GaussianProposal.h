#ifndef GAUSSIANPROPOSAL_H
#define GAUSSIANPROPOSAL_H

#include "ProposalDistribution.h"
#include <random>
#include <iostream>
#define M_PI        3.14159265358979323846264338327950288   /* pi             */

class GaussianProposal : public ProposalDistribution {
public:
    GaussianProposal(float standardDeviation);
    ~GaussianProposal();

    Eigen::VectorXf propose(Eigen::VectorXf params) override;
    float evaluateLogTransitionProbability(Eigen::VectorXf fromParams, Eigen::VectorXf toParams) override;

private:
    std::default_random_engine generator;
    std::normal_distribution<float> distribution{0.0, 1.0};
};

#endif // GAUSSIANPROPOSAL_H