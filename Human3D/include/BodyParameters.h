#ifndef BODYPARAMETERS_H
#define BODYPARAMETERS_H


class BodyParameters {
public:
    BodyParameters() { }
    ~BodyParameters() { }

    float armSpan;
    float shoulderWidth;
    float chestWidth;
    float thighWidth;
    float stomachWidth;
    float legHeight;
    float height;
    float neckLength;
    float headWidth;
    float headIntoLength;
    float thighRighWidth;

    // ratios
    float armSpanRatio;
    float shoulderWidthRatio;
    float chestWidthRatio;
    float thighWidthRatio;
    float stomachWidthRatio;
    float legHeightRatio;
    float heightRatio;
    float neckLengthRatio;
    float headWidthRatio;
    float headIntoLengthRatio;
    float thighRightWidthRatio;
};

#endif // BODYPARAMETERS_H