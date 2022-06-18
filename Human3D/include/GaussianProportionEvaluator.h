#ifndef GAUSSIANPROPORTIONEVALUATOR_H
#define GAUSSIANPROPORTIONEVALUATOR_H


#include "BodyParameters.h"
#include <cmath>
#define M_PI        3.14159265358979323846264338327950288   /* pi             */

/**
 * @brief gaussian likelihood evalutator for body parameters
 * 
 */
class GaussianProportionEvaluator {
public:
    /**
     * @brief sums of all logs of the normal distribution for each body parameter
     * 
     * @param observedParams    - the input body parameters from the 2D image
     * @param calculatedParams  - calculated body parameters from the shape model
     * 
     * @return float
     */
    static float evaluateLogProportions(float standardDeviation, BodyParameters observedParams, BodyParameters calculatedParams);

};

#endif // GAUSSIANPROPORTIONEVALUATOR_H