#include "GaussianProportionEvaluator.h"

float GaussianProportionEvaluator::evaluateLogProportions(float standardDeviation, BodyParameters observedParams, BodyParameters calculatedParams) {
    // mean: calculatedParam
    // x: observedParam

    // float denom = -0.5 * log(2 * M_PI) - log(standardDeviation);
    
    // float diffSquaredArmSpan =  (observedParams.armSpan - calculatedParams.armSpan) * (observedParams.armSpan - calculatedParams.armSpan);
    // float valueArmSpan = denom - 0.5 * diffSquaredArmSpan / (standardDeviation * standardDeviation);

    // float diffSquaredHeight =  (observedParams.height - calculatedParams.height) * (observedParams.height - calculatedParams.height);
    // float valueHeight = denom - 0.5 * diffSquaredHeight / (standardDeviation * standardDeviation);

    // return valueArmSpan + valueHeight;

    float denom = -0.5 * log(2 * M_PI) - log(standardDeviation);
    
    float diffSquaredArmSpan =  (observedParams.armSpanRatio - calculatedParams.armSpanRatio) * (observedParams.armSpanRatio - calculatedParams.armSpanRatio);
    float valueArmSpan = denom - 0.5 * diffSquaredArmSpan / (standardDeviation * standardDeviation);

  
    float diffSquaredStomachWidth =  (observedParams.stomachWidthRatio - calculatedParams.stomachWidthRatio) * (observedParams.stomachWidthRatio - calculatedParams.stomachWidthRatio);
    float valueStomachWidth = denom - 0.5 * diffSquaredStomachWidth / (standardDeviation * standardDeviation);

    float diffSquaredChestWidth =  (observedParams.chestWidthRatio - calculatedParams.chestWidthRatio) * (observedParams.chestWidthRatio - calculatedParams.chestWidthRatio);
    float valueChestWidth = denom - 0.5 * diffSquaredChestWidth / (standardDeviation * standardDeviation);

    float diffLegHeight =  (observedParams.legHeightRatio - calculatedParams.legHeightRatio) * (observedParams.legHeightRatio - calculatedParams.legHeightRatio);
    float valueLegHeight = denom - 0.5 * diffLegHeight / (standardDeviation * standardDeviation);

    float diffNeckHeight =  (observedParams.neckLengthRatio - calculatedParams.neckLengthRatio) * (observedParams.neckLengthRatio - calculatedParams.neckLengthRatio);
    float valueNeckHeight = denom - 0.5 * diffNeckHeight / (standardDeviation * standardDeviation);

    float diffHeadWidth =  (observedParams.headWidthRatio - calculatedParams.headWidthRatio) * (observedParams.headWidthRatio - calculatedParams.headWidthRatio);
    float valueHeadWidth = denom - 0.5 * diffHeadWidth / (standardDeviation * standardDeviation);

    float diffHeadInto =  (observedParams.headIntoLengthRatio - calculatedParams.headIntoLengthRatio) * (observedParams.headIntoLengthRatio - calculatedParams.headIntoLengthRatio);
    float valueHeadInto = 0.0;//denom - 0.5 * diffHeadInto / (standardDeviation * standardDeviation);

    float diffThighRightWidth =  (observedParams.thighRightWidthRatio - calculatedParams.thighRightWidthRatio) * (observedParams.thighRightWidthRatio - calculatedParams.thighRightWidthRatio);
    float valueThighRightWidth = denom - 0.5 * diffThighRightWidth / (standardDeviation * standardDeviation);

    // float diffHeight =  (observedParams.heightRatio - calculatedParams.heightRatio) * (observedParams.heightRatio - calculatedParams.heightRatio);
    // float valueHeight = denom - 0.5 * diffHeight / (standardDeviation * standardDeviation);


    //return valueArmSpan  + valueStomachWidth + valueChestWidth + valueLegHeight + valueNeckHeight + valueHeadWidth + valueHeadInto;
    return valueArmSpan  + valueStomachWidth + valueChestWidth + valueLegHeight + valueHeadWidth + valueThighRightWidth + valueNeckHeight;
    //return valueArmSpan + valueStomachWidth + valueChestWidth + valueHeadWidth;
}

