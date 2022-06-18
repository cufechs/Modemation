#ifndef PCA_H
#define PCA_H

#include "Model.h"
#include "DeformationField.h"
#include <Eigen/SVD>
#include <Eigen/Dense>
#include <cmath>
#include <Eigen/Eigenvalues>

class PCA {
public:
    PCA(std::vector<Model> models);
    PCA(std::vector<std::vector<DeformationField>> defFields);
    ~PCA();

    Eigen::MatrixXf getData() const;
    // compute eigen vectors and values
    void computeEig();

    Eigen::VectorXf getEigenValues() const;
    Eigen::MatrixXf getTopKEigenVectors(int k) const;
    Eigen::VectorXf getProjection(Eigen::VectorXf vec) const;
    Eigen::VectorXf getMean() const;
    Eigen::MatrixXf getEigenVectors() const;

private:  
    Eigen::MatrixXf data; // original data
    Eigen::MatrixXf eigenVectors;
    Eigen::VectorXf mean;
    Eigen::VectorXf eigenVector;
    Eigen::VectorXf eigenValues;

    // rows and cols of original data
    unsigned int nrows;
    unsigned int ncols;


};

#endif // PCA_H