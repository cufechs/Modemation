#include "Alignment.h"

void Alignment::RotationAlignment(Model &from, Model to) {

    glm::vec3 fromVec = from.mesh.getPointAtIndex(9008).position;
    glm::vec3 toVec = to.mesh.getPointAtIndex(9008).position;

    glm::vec3 v = glm::cross(toVec, fromVec);
    if (v.x == 0.0 && v.y == 0.0 && v.z == 0.0) {
        std::cout << "[Alignment::RotationAlignment]::no rotation needed\n";
        return;
    }

    float angle = acos(glm::dot(toVec, fromVec) / (glm::length(toVec) * glm::length(fromVec)));

    glm::mat4 rotmat = glm::rotate(angle, v);

    // special cases lead to NaN values in the rotation matrix
    if (glm::any(glm::isnan(rotmat * glm::vec4(1.0f, 1.0f, 1.0f, 1.0f)))) {
        if (angle < 0.1f) {
            rotmat = glm::mat4(1.0f);
        }
        else if (angle > 3.1f) {
            // rotate about any perpendicular vector
            rotmat = glm::rotate(angle, glm::cross(fromVec,
                                        glm::vec3(fromVec.y, fromVec.z, fromVec.x)));
        }
        else {
            assert(false);
        }
    }

    // rotate all the points in the "from" mesh by the calculated rotation matrix
    for (int i = 0; i < from.mesh.points.size(); i++) {
        from.mesh.points[i].position = rotmat * glm::vec4(from.mesh.points[i].position, 1.0f);        
    }

    // rotate all normals in "from" mesh
    for (int i = 0; i < from.mesh.normals.size(); i++) {
        from.mesh.normals[i].position = rotmat * glm::vec4(from.mesh.normals[i].position, 1.0f);
    }

}

float Alignment::procrustesDistance(Model m, Model reference) {

    float sumSquareDistance = 0.0f;
    for (int i = 0; i < m.mesh.points.size(); i++) {
        sumSquareDistance += (pow(reference.mesh.points[i].position.x - m.mesh.points[i].position.x, 2) +
            pow(reference.mesh.points[i].position.y - m.mesh.points[i].position.y, 2) +
            pow(reference.mesh.points[i].position.z - m.mesh.points[i].position.z, 2));
    }

    sumSquareDistance = sqrt(sumSquareDistance);
    return sumSquareDistance;
}

void Alignment::ICP(Model& from, Model to) {

    Eigen::MatrixXf toMat(from.mesh.points.size(), 3);
    for (int i = 0; i < to.mesh.points.size(); i++) {
        toMat(i, 0) = to.mesh.points[i].position.x;
        toMat(i, 1) = to.mesh.points[i].position.y;
        toMat(i, 2) = to.mesh.points[i].position.z;
    }

    for (int j = 0; j < 1; j++) {
        std::cout << "[Alignment::ICP]::................. iteration #" << j << " .....................\n";
        Eigen::MatrixXf fromMat(from.mesh.points.size(), 3);
        
        // initialize the eigen matrix
        for (int i = 0; i < from.mesh.points.size(); i++) {
            fromMat(i, 0) = from.mesh.points[i].position.x;
            fromMat(i, 1) = from.mesh.points[i].position.y;
            fromMat(i, 2) = from.mesh.points[i].position.z;
        }

        // compute the covariance matrix
        Eigen::MatrixXf cov = (toMat.transpose() * fromMat) / (from.mesh.points.size()-1);
        for (int i = 0; i < 3; i++) {
            for (int j = 0; j < 3; j++) {
                std::cout << cov(i,j) << " ";
            }
            std::cout << "\n";
        }
 
        // compute the singular value decomposition of the covariance matrix
        Eigen::JacobiSVD<Eigen::MatrixXf> svd(cov, Eigen::ComputeThinU | Eigen::ComputeThinV);

        Eigen::MatrixXf matU = svd.matrixU();
        Eigen::MatrixXf matV = svd.matrixV();

        glm::vec3 fromCenterOfMass = from.mesh.getCenterOfMass();
        glm::vec3 toCenterOfMass = to.mesh.getCenterOfMass();

        Eigen::MatrixXf rotationMatrix = matU * matV.transpose();

        glm::mat3x3 rotMat;
        for (int i = 0; i < 3; i++)
            for (int j = 0; j < 3; j++)
                rotMat[i][j] = rotationMatrix(i, j);

        glm::vec3 t = toCenterOfMass - rotMat * fromCenterOfMass;

        // apply rotation on "from" Model
        for (int i = 0; i < from.mesh.points.size(); i++) {
            from.mesh.points[i].position = rotMat * from.mesh.points[i].position + t;        
        }

        // rotate all normals in "from" mesh
        for (int i = 0; i < from.mesh.normals.size(); i++) {
            from.mesh.normals[i].position = rotMat * from.mesh.normals[i].position + t;
        }

        std::cout << "[Alignment::ICP]::distance error: " << procrustesDistance(from, to) << "\n";

    }
    
}