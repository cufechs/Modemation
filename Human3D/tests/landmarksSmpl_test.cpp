#include <iostream>
#include <vector>
#include <string>
#include <fstream>
#include <json/json.hpp>
#include <typeinfo>
#include "ObjLoader.h"


unsigned int getNearestIndex(std::vector<Point<glm::vec3>> points, glm::vec3 coordinate) {
    float error = 9999999.0f;
    unsigned int index = -1;
    for (int i = 0; i < points.size(); i++) {
        glm::vec3 point = points[i].position;
        float e = glm::distance(point, coordinate);
        if (e < error) {
            error = e;
            //std::cout << "error in loop: " << error << "\n";
            index = i;
        }
    }
    return index;
}


int main() {

    // load landmarks created from blender
    std::string filename = "/Users/abdelrahmanabdelghany/Documents/college/semester10/GP/Human3D/data/smpl/landmarks_smpl.json";
    std::ifstream json_file(filename);
    // read as json file
    nlohmann::json json;
    json_file >> json;
    json_file.close();

    // reference mesh at which the landmarks defined on
    std::string obj_file = "/Users/abdelrahmanabdelghany/Documents/college/semester10/GP/Human3D/data/smpl/smpl_uv.obj";
    
    // obj loading related variables
    std::vector<Point<glm::vec3>> points;
    std::vector<unsigned int> pointIds; 
    std::vector<TriangleCell> faces;
    std::vector<Point<glm::vec3>> normals;
    std::vector<Point<glm::vec2>> texCoords;

    // load referenceObj into points and the other variables
    //ObjLoader::loadObj(obj_file, points, pointIds, faces, normals, texCoords);
    ObjLoader::readSmplUVRef(obj_file, points, faces, texCoords);

    std::cout << "number of points: " << points.size() << "\n";

    // json index
    int k = 0;

    // file to store the id and its corresponding vertex index in the obj file
    nlohmann::json ids_index_json;

    // iterate on the input landmarks file
    for (nlohmann::json::iterator it = json.begin(); it != json.end(); ++it) {
        std::cout << *it << '\n';

        // read coordinates of the current object
        float x = (*it)["coordinates"][0];
        float y = (*it)["coordinates"][1];
        float z = (*it)["coordinates"][2];

        glm::vec3 coordinate = glm::vec3(x, y, z);
        // get the index corresponding to this coordinate
        unsigned int index = getNearestIndex(points, coordinate);

        // add the id and index as entry in the output json file
        ids_index_json[k]["id"] = (*it)["id"];
        ids_index_json[k]["index"] = index;
        k++;
    }

    // save the output json file
    std::ofstream writeJson("/Users/abdelrahmanabdelghany/Documents/college/semester10/GP/Human3D/data/smpl/ids_index_smpl.json");
    writeJson << std::setw(4) << ids_index_json << std::endl;

    std::cout << "done landmarks test.\n";
    return 0;
}