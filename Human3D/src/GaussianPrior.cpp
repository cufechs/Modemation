#include "GaussianPrior.h"

// here we are assuming an isotropic gaussian (i.e covariance matrix is diagonal, i.e all thetas are independent of each other)
float GaussianPrior::evaluateLogPrior(float mean, float standardDeviation, Eigen::VectorXf coefficients) {

    float denom = -0.5 * log(2 * M_PI) * coefficients.size() - coefficients.size() * log(standardDeviation);

    float sumDiff = 0.0;
    for (int i = 0; i < coefficients.size(); i++) {
        sumDiff += ( (coefficients[i] - mean) * (coefficients[i] - mean) ) / (standardDeviation * standardDeviation);
    }

    return denom - 0.5 * sumDiff;
}

float GaussianPrior::evaluatePrior(float mean, float standardDeviation, Eigen::VectorXf coefficients) {

    float denom = -0.5 * log(2 * M_PI) * coefficients.size() - coefficients.size() * log(standardDeviation);

    float sumDiff = 0.0;
    for (int i = 0; i < coefficients.size(); i++) {
        sumDiff += ( (coefficients[i] - mean) * (coefficients[i] - mean) ) / (standardDeviation * standardDeviation);
    }

    return denom - 0.5 * sumDiff;
}