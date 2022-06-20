#include "Model.h"
#include <iostream> 
#include <unordered_map>
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

    std::cout << "[Model] included successfully\n";

    Model model("/Users/abdelrahmanabdelghany/Documents/college/semester10/GP/Human3D/tests/cube2.obj");
    
    std::cout << "[Model] loaded .obj file successfully\n";
    std::cout << "[Model] model.mesh.points.size(): " << model.mesh.pointIds.size() << "\n";
    printMesh(model.mesh);

    ObjLoader::saveObj("/Users/abdelrahmanabdelghany/Documents/college/semester10/GP/Human3D/tests/cubeNew.obj",
        model.mesh.points, model.mesh.pointIds, model.mesh.triangleCells, model.mesh.normals, model.mesh.textureCoords);

    return 0;
}
