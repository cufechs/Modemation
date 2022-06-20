#ifndef ALIGNMENT_H
#define ALIGNMENT_H

#include "Model.h"
#include <glm/gtx/euler_angles.hpp>
#include <glm/gtc/matrix_transform.hpp>
#include <glm/gtx/transform.hpp>
#include <iostream>
#include <cmath>
#include <Eigen/Dense>
#include <Eigen/SVD>


class Alignment {
public: 
    /**
     * @brief aligns the from Model on the to Model using a simple rotation matrix
     *        on one correspondant point between the two models
     * 
     * @param from  - model to be aligned
     * @param to    - model to be aligned on
     */
    static void RotationAlignment(Model &from, Model to);

    /**
     * @brief caclulates the procrustes distance between two models as a measure of how aligned they are
     * 
     * @param m             - arbitrary model
     * @param reference     - reference model to see how far "m" model is from it
     * @return float        - procurstes distance
     */
    static float procrustesDistance(Model m, Model reference);

    /**
     * @brief Iterative closest point algorithm using SVD
     * 
     * @param from  - model to be aligned
     * @param to    - model to be aligned on
     */
    static void ICP(Model& from, Model to);
};

#endif // ALIGNMENT_H