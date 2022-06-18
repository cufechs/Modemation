#include "MetropolisHastings.h"


MetropolisHastings::MetropolisHastings(BuildSSM* shapeModel, const std::string& inputParamsPath, Eigen::VectorXf initCoefficients, float proposalStddev, float likelihoodStddev, float priorStddev) {
    ssm = shapeModel;
    shapeCoefficients = initCoefficients;
    proposalDistribution = new GaussianProposal(proposalStddev);
    this->likelihoodStddev = likelihoodStddev;
    this->priorStddev = priorStddev;

    std::ifstream json_file(inputParamsPath);
    // read as json file
    json_file >> this->observedParamsJson;
    json_file.close();

    observedBodyParams.height = (float)observedParamsJson["height"];
    observedBodyParams.armSpan = (float)observedParamsJson["arm_span"];
    observedBodyParams.stomachWidth = (float)observedParamsJson["belly"];
    observedBodyParams.thighRighWidth = (float)observedParamsJson["thigh"];
    observedBodyParams.chestWidth = (float)observedParamsJson["chest_width"];
    observedBodyParams.legHeight = (float)observedParamsJson["leg_length"];
    observedBodyParams.headWidth = (float)observedParamsJson["head_width"];

    observedBodyParams.armSpanRatio = (float)observedBodyParams.armSpan / (float)observedBodyParams.height;
    observedBodyParams.stomachWidthRatio = (float)observedBodyParams.stomachWidth / (float)observedBodyParams.height;
    observedBodyParams.thighRightWidthRatio = (float)observedBodyParams.thighRighWidth / (float)observedBodyParams.height;
    observedBodyParams.chestWidthRatio = (float)observedBodyParams.chestWidth / (float)observedBodyParams.height;
    observedBodyParams.legHeightRatio = (float)observedBodyParams.legHeight / (float)observedBodyParams.height;
    observedBodyParams.headWidthRatio = (float)observedBodyParams.headWidth / (float)observedBodyParams.height;
    observedBodyParams.neckLengthRatio = 0.03f;

}

MetropolisHastings::~MetropolisHastings() {

}

Model MetropolisHastings::run(unsigned int iterations) {
    std::vector<int> indices;
    int lastIndex = 0;

    float bestAlpha = -99999999.99;
    Eigen::VectorXf bestCoef = shapeCoefficients;
    int countAccepted = 0;
    int countRejected = 0;
    nlohmann::json idsIndicesJson = ssm->getIdsIndicesJson();

    // uniform distribution
    std::random_device rand_dev;
    unsigned seed = 0;
    std::mt19937 generator(seed);
    std::uniform_real_distribution<> uniform_dist(0, 1);
    //srand( (unsigned)time( NULL ) );

    for (int i = 0; i < iterations; i++) {
        std::cout << "......... iteration #: " << i+1 << " / "<< iterations<<" ............\n";
        // 1.
        Eigen::VectorXf proposalShapeCoeff = proposalDistribution->propose(shapeCoefficients);
        // 2.
        Mesh meshInstance = ssm->instanceNoNormals(shapeCoefficients);
        meshInstance.scale(1000.0);
        Model modelInstance(meshInstance, idsIndicesJson);
        
        BodyParameters calculatedBodyParams = modelInstance.computeBodyRatios();//modelInstance.computeBodyParameters();
        

        float likelihood = GaussianProportionEvaluator::evaluateLogProportions(likelihoodStddev, observedBodyParams, calculatedBodyParams);
        float prior = GaussianPrior::evaluateLogPrior(0.0, priorStddev, shapeCoefficients);
        float posterior = likelihood + prior;

        // 3. 
        Mesh proposedMesh = ssm->instanceNoNormals(proposalShapeCoeff);
        proposedMesh.scale(1000.0);

        // 4.
        Model proposedModel(proposedMesh, idsIndicesJson);
        // 5.
        BodyParameters proposedBodyParameters = proposedModel.computeBodyRatios();//proposedModel.computeBodyParameters();

        // 6. 
        float likelihoodProposed = GaussianProportionEvaluator::evaluateLogProportions(likelihoodStddev, observedBodyParams, proposedBodyParameters);
        float priorProposed = GaussianPrior::evaluateLogPrior(0.0, priorStddev, proposalShapeCoeff);
        float posteriorProposed = likelihoodProposed + priorProposed;

        // 7.
        float transitionProbRatio = proposalDistribution->evaluateLogTransitionProbability(shapeCoefficients, proposalShapeCoeff);

        float alpha = posteriorProposed - posterior - transitionProbRatio; //min(0, ...) and do not check if alpha > 0 then
        //alpha = std::min(0.0f, alpha);
      
        //srand( (unsigned)time( NULL ) );
        //float u = (float) rand()/RAND_MAX;
        float u = uniform_dist(generator);
        

        if (alpha > 0 || exp(alpha) > u) {
            countAccepted++;
            shapeCoefficients = proposalShapeCoeff;

            bestAlpha = alpha;
            bestCoef = shapeCoefficients;
            indices.push_back(i);
            lastIndex = i;
        } else {
            countRejected++;
        }

        if (i - lastIndex > 1690) {
            break;
        }

        
    }

    std::cout << "\n*********** countAccepted: " << countAccepted << "\n";
    std::cout << "*********** countRejected: " << countRejected << "\n";
    Mesh finalMesh = ssm->instance(bestCoef);
    finalMesh.scale(1000.0);
    Model finalModel(finalMesh, idsIndicesJson);

    BodyParameters finalBodyParameters = finalModel.computeBodyRatios();//finalModel.computeBodyParameters();
    std::cout << "finalBodyParameters: \n";
    std::cout << "finalBodyParameters.armSpan; " << finalBodyParameters.armSpan << "\n";
    std::cout << "finalBodyParameters.shoulderWidth; " << finalBodyParameters.shoulderWidth << "\n";
    std::cout << "finalBodyParameters.height; " << finalBodyParameters.height << "\n";

    std::cout << "finalBodyParameters.armSpanRatio; " << finalBodyParameters.armSpanRatio << "\n";
    //std::cout << "finalBodyParameters.shoulderWidthRatio; " << finalBodyParameters.shoulderWidthRatio << "\n";
    std::cout << "finalBodyParameters.stomachWidthRatio; " << finalBodyParameters.stomachWidthRatio << "\n";
    std::cout << "finalBodyParameters.chestWidthRatio; " << finalBodyParameters.chestWidthRatio << "\n";
    std::cout << "finalBodyParameters.legHeightRatio; " << finalBodyParameters.legHeightRatio << "\n";
    std::cout << "finalBodyParameters.neckLengthRatio; " << finalBodyParameters.neckLengthRatio << "\n";
    std::cout << "finalBodyParameters.headWidthRatio; " << finalBodyParameters.headWidthRatio << "\n";
    std::cout << "finalBodyParameters.thighRightWidthRatio; " << finalBodyParameters.thighRightWidthRatio << "\n";
   //std::cout << "finalBodyParameters.headIntoLengthRatio; " << finalBodyParameters.headIntoLengthRatio << "\n";
    //std::cout << "finalBodyParameters.heightRatio; " << finalBodyParameters.heightRatio << "\n";
    
    // std::cout << "indices accepted: ";
    // for (int i = 0; i < indices.size(); i++) std::cout << indices[i] << " ";
    // std::cout << "\n";

    return finalModel;

}