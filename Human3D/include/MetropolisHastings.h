#ifndef METROPOLISHASTINGS_H
#define METROPOLISHASTINGS_H

#include <string>
#include <fstream>
#include <json/json.hpp>
#include <iostream>
#include <time.h>
#include <algorithm>
#include "BuildSSM.h"
#include "BodyParameters.h"
#include "GaussianPrior.h"
#include "GaussianProportionEvaluator.h"
#include "GaussianProposal.h"

class MetropolisHastings {
public:
    MetropolisHastings(BuildSSM* shapeModel, const std::string& inputParamsPath, Eigen::VectorXf initCoefficients, float proposalStddev, float likelihoodStddev, float priorStddev);
    ~MetropolisHastings();

    Model run(unsigned int iterations);

    nlohmann::json observedParamsJson;
private:
    BuildSSM* ssm;
    Eigen::VectorXf shapeCoefficients;
    BodyParameters observedBodyParams;
    GaussianProposal* proposalDistribution;
    float likelihoodStddev;
    float priorStddev;
};

#endif // METROPOLISHASTINGS_H