#include <iostream>
#include <glm/glm.hpp>
#include <glm/gtx/normal.hpp>
#include <Eigen/Dense>


using namespace std;

int main () {

    // glm::matrix m(1,2,3,4,5,6,7,8);
    glm::mat4 myIdentityMatrix = glm::mat4(1.0f);

    
    // rows: 4, columns: 3
    glm::mat<4, 3, float, glm::defaultp> mat43;//(1,2,3,4,5,6,7,8,9,10,11,12);

    for (int i = 0; i < 4; i++) {
        for (int j = 0; j < 3; j++) {
            mat43[1][j] = i + j;
            cout << mat43[i][j] << ", ";
        }
        cout << "\n";
    }

    // v: 4,2,1
    glm::vec3 computedNormal = glm::triangleNormal(glm::vec3(0.066264f,0.317279f,-0.011677f), glm::vec3(0.070060f, 0.314932f, -0.010866f), glm::vec3(0.065918f, 0.315907f, -0.011918f));
    // glm::vec3 computedNormal = glm::triangleNormal(glm::vec3(-1,1,-1), glm::vec3(1,1,1), glm::vec3(1,1,-1));
    cout << "computedNormal: (" << computedNormal.x << ", " << computedNormal.y << ", " << computedNormal.z << ")\n";

    Eigen::MatrixXd m(2,2);
    m(0,0) = 3;
    m(1,0) = 2.5;
    m(0,1) = -1;
    m(1,1) = m(1,0) + m(0,1);
    std::cout << m << std::endl;


    Eigen::MatrixXd P(3,3);
    std::cout << "P matrix: " << P << std::endl;
    std::cout << "*********\n";
    P << 6, 0, 0, 0, 4, 0, 0, 0, 7;
    std::cout << "P matrix: " << P << std::endl;
    std::cout << "*********\n";
    Eigen::MatrixXd L( P.llt().matrixL() );
    std::cout << L.col(0) << std::endl;
    

    cout << "done\n";
    return 0;
}