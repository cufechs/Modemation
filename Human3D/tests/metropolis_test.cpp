#include <iostream>
#include "MetropolisHastings.h"


int main() {

    std::cout << "metropolis included successfully\n";

    BuildSSM ssm;
    // ssm.loadPCAModel("/Users/abdelrahmanabdelghany/Documents/college/semester10/GP/Human3D/tests/pcaModel_male_630_smpl_T.h5",
    //     "/Users/abdelrahmanabdelghany/Documents/college/semester10/GP/Human3D/data/smpl/smpl_uv.obj");
    // ssm.readIdsIndicesLandmarks("/Users/abdelrahmanabdelghany/Documents/college/semester10/GP/Human3D/data/smpl/ids_index_smpl.json");

    ssm.loadPCAModel("/Users/abdelrahmanabdelghany/Documents/college/semester10/GP/Human3D/tests/pcaModel_male_630_smplx_v2_T.h5",
        "/Users/abdelrahmanabdelghany/Documents/college/semester10/GP/Human3D/tests/referenceObj.obj");
    ssm.readIdsIndicesLandmarks("/Users/abdelrahmanabdelghany/Documents/college/semester10/GP/Human3D/tests/ids_index_v2.json");

    BodyParameters observedParams;

    // define the ratios in the image
    // observedParams.height = 492.0;
    // observedParams.armSpanRatio = 497.0/492.0; // 1.01
    // observedParams.shoulderWidthRatio = 101.0/492.0; // 0.205
    // observedParams.thighWidthRatio = 41.0/492.0; // 0.08333
    // observedParams.stomachWidthRatio = 75.0/492.0; // 0.152439  
    // observedParams.chestWidthRatio = 97.0/492.0; // 0.19715
    // observedParams.legHeightRatio = 240.0/492.0; // 0.4878
    // //observedParams.neckLengthRatio = 26.0/492.0; // 0.046747
    // observedParams.headWidthRatio = 44.0/492.0; // 0.08943
    //observedParams.headIntoLengthRatio = 66.0/492.0;


    // observedParams.height = 868.0;
    // observedParams.armSpanRatio = 758.0/868.0; // 0.87327
    // //observedParams.shoulderWidthRatio = 101.0/868.0; // 0.205
    // observedParams.thighRightWidthRatio = 83.0/868.0; // 0.0956
    // observedParams.stomachWidthRatio = 173.0/868.0; // 0.199308  
    // observedParams.chestWidthRatio = 185.0/868.0; // 0.21313
    // observedParams.legHeightRatio = 456.0/868.0; // 0.525345
    // observedParams.headWidthRatio = 82.0/868.0; // 0.0.09447

    observedParams.height = 492.0;
    observedParams.armSpanRatio = 497.0/492.0; // 0.87327
    //observedParams.shoulderWidthRatio = 101.0/868.0; // 0.205
    observedParams.thighRightWidthRatio = 41.0/492.0; // 0.0956
    observedParams.stomachWidthRatio = 75.0/492.0; // 0.199308  
    observedParams.chestWidthRatio = 97.0/492.0; // 0.21313
    observedParams.legHeightRatio = 240.0/492.0; // 0.525345
    observedParams.headWidthRatio = 44.0/492.0; // 0.0.09447
    observedParams.neckLengthRatio = 0.030;

    Eigen::VectorXf coefficients(7);
    coefficients.setZero();
    //MetropolisHastings metropolis(&ssm, coefficients, observedParams, 0.34, 0.2, 1.0);
    //MetropolisHastings metropolis(&ssm, coefficients, observedParams, 0.165, 1.0, 1.0); //u(0,1)
    MetropolisHastings metropolis(&ssm, coefficients, observedParams, 0.066f, 0.01f, 1.0f);
    metropolis.run(7000);

    return 0;
}