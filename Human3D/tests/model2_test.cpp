#include "Model.h"
#include <iostream> 
#include <fstream>
#include <glm/glm.hpp>




void printMesh(Mesh m) {
    for (int i = 0; i < m.points.size(); i++) {
        std::cout << "point: (" << 
            m.points[i].getPosition().x << ", " <<
            m.points[i].getPosition().y << ", " <<
            m.points[i].getPosition().z << ")\n";
        
    }
}

int main() {

    nlohmann::json idsIndicesJson;
    std::ifstream json_file("/Users/abdelrahmanabdelghany/Documents/college/semester10/GP/Human3D/data/smpl/ids_index_smpl.json");
    // read as json file
    json_file >> idsIndicesJson;
    json_file.close();

    std::cout << "idsIndicesJson.size(): " << idsIndicesJson.size() << "\n";
    std::cout << "[Model] included successfully\n";

    Model model("/Users/abdelrahmanabdelghany/Documents/college/semester10/GP/Human3D/tests/meshTestSampledFromSavedModel_630.obj");
    model.computeLandmarksPositions(idsIndicesJson);

    float height = model.computeModelHeight();
    float armSpan = model.computeArmSpan();
    float shoulderWidth = model.computeShoulderWidth();
    std::cout << "height: " << height << "\n";
    std::cout << "armSpan: " << armSpan << "\n";
    std::cout << "shoulderWidth: " << shoulderWidth << "\n";

    return 0;
}
