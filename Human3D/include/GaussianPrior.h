#ifndef GAUSSIANPRIOR_H
#define GAUSSIANPRIOR_H

#include <Eigen/Dense>
#include <math.h>
#define M_PI        3.14159265358979323846264338327950288   /* pi             */

class GaussianPrior {
public:
    static float evaluateLogPrior(float mean, float standardDeviation, Eigen::VectorXf coefficients);
    static float evaluatePrior(float mean, float standardDeviation, Eigen::VectorXf coefficients);
};

#endif // GAUSSIANPRIOR_H