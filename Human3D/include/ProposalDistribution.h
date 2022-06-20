#ifndef PROPOSALDISTRIBUTION_H
#define PROPOSALDISTRIBUTION_H

#include <Eigen/Dense>

class ProposalDistribution {
public:
    ProposalDistribution(float standardDeviation) {
        this->standardDeviation = standardDeviation;
    }
    // add a random walk perturbation to params using standard deviation and a gaussian number
    // i.e foreach x in params: x = x + standardDeviation * randomGaussian
    virtual Eigen::VectorXf propose(Eigen::VectorXf params) = 0;
    virtual float evaluateLogTransitionProbability(Eigen::VectorXf fromParams, Eigen::VectorXf toParams) = 0;

protected:
    float standardDeviation;
};


#endif // PROPOSALDISTRIBUTION_H