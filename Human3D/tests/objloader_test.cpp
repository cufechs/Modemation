#include "ObjLoader.h"


int main() {

    std::cout << "[ObjLoader] imported successfully\n";
    std::string obj_path = "/Users/abdelrahmanabdelghany/Documents/college/semester10/GP/Human3D/tests/cube2.obj";
    std::vector<Point<glm::vec3>> points;
    std::vector<unsigned int> pointIds; 
    std::vector<TriangleCell> faces;
    std::vector<Point<glm::vec3>> normals;
    std::vector<Point<glm::vec2>> texCoords;

    ObjLoader::loadObj(obj_path, points, pointIds, faces, normals, texCoords);

    for (int i = 0; i < points.size(); i++) {
        std::cout << "point: (" << 
            points[i].getPosition().x << ", " <<
            points[i].getPosition().y << ", " <<
            points[i].getPosition().z << ")\n";
        
    }
    std::cout << "pointIds.size(): " << pointIds.size() << "\n";

    std::cout << "[ObjLoader]::loadModel: points loaded correctly\n";

    return 0;
}