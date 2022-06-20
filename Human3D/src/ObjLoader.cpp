#include "ObjLoader.h"

int ObjLoader::x = 0;
std::vector<Point<glm::vec2>> smplTexCoords = {};
std::vector<TriangleCell> smplFaces = {};

void ObjLoader::loadObj(std::string obj_path, std::vector<Point<glm::vec3>>& _points, std::vector<unsigned int>& pointIds, std::vector<TriangleCell>& _faces, std::vector<Point<glm::vec3>>& _normals, std::vector<Point<glm::vec2>>& _texCoords) {
    x = 1;
    std::vector<std::string*> _positions;

    std::fstream file_in(obj_path);
    if (!file_in.is_open()) {
        std::cout << "[ObjLoader::loadModel] cannot load obj file\n";
        return;
    }
    //std::cout << "obj_path" << obj_path << "\n";
    char buffer[256];
    while (!file_in.eof()) {
        file_in.getline(buffer, 256);
        _positions.push_back(new std::string(buffer));
    }

    unsigned int vertexIndex = 0;
    unsigned int normalIndex = 0;
    unsigned int triangleIndex = 0;
    unsigned int textureIndex = 0;
    for (int i = 0; i < _positions.size(); i++) {
        if (_positions[i]->c_str()[0] == '#') {
            continue;
        } else if (_positions[i]->c_str()[0] == 'v' && _positions[i]->c_str()[1] == ' ') {
            glm::vec3 pos;
            sscanf(_positions[i]->c_str(), "v %f %f %f", &pos.x, &pos.y, &pos.z);
            //std::cout << "pos.x: " << pos.x << "\n";
            _points.push_back(Point(pos, vertexIndex));
            pointIds.push_back(vertexIndex);
            vertexIndex += 1;
        } else if (_positions[i]->c_str()[0] == 'v' && _positions[i]->c_str()[1] == 'n') {
            glm::vec3 normal;
            sscanf(_positions[i]->c_str(), "vn %f %f %f", &normal.x, &normal.y, &normal.z);

            _normals.push_back(Point(normal, vertexIndex));
            normalIndex += 1;
        } else if (_positions[i]->c_str()[0] == 'v' && _positions[i]->c_str()[1] == 't') {
            glm::vec2 texCoord;
            sscanf(_positions[i]->c_str(), "vt %f %f", &texCoord.x, &texCoord.y);

            _texCoords.push_back(Point(texCoord, textureIndex));
            textureIndex += 1;
        } else if (_positions[i]->c_str()[0] == 'f') {
            unsigned int v1,v2,v3, n1, vt1,vt2,vt3;

            sscanf(_positions[i]->c_str(), "f %d/%d/%d %d/%d/%d %d/%d/%d", 
                   &v1,&vt1,&n1, &v2,&vt2,&n1, &v3,&vt3,&n1);
            //std::cout << "v1: " << v1 << ", v2: " << v2 << ", v3: " << v3 << "\n";
            _faces.push_back(TriangleCell(v1-1,v2-1,v3-1,n1-1,triangleIndex,vt1-1,vt2-1,vt3-1));
            triangleIndex += 1;
        }
        
    }

    // cleanup
    for (int i = 0; i < _positions.size(); i++) 
        delete _positions[i];

}

void ObjLoader::saveObj(std::string obj_path, std::vector<Point<glm::vec3>> points, std::vector<unsigned int> pointIds, std::vector<TriangleCell> faces, std::vector<Point<glm::vec3>> normals, std::vector<Point<glm::vec2>> textureCoords) {
    // all obj files that will be written have the same headerText, textBeforeFaces, and textureCoords
    std::string headerText = "# Blender v2.81 (sub 16) OBJ File: 'smplx_gen.blend'\n# www.blender.org\nmtllib 1_human.mtl\no SMPLX-mesh-male_SMPLX-shapes-male.001\n";
    std::string textBeforeFaces = "usemtl SMPLX-male.001\ns 1\n";

    std::ofstream objFile;
    objFile.open(obj_path);

    objFile << headerText;

    // write vertices positions
    for (int i = 0; i < points.size(); i++) {
        std::string v = std::string("v") + std::string(" ") + convertToString(float(points[i].position.x)) + " " + convertToString(float(points[i].position.y)) + " " +
                        convertToString(float(points[i].position.z)) + "\n";
        objFile << v;
    }

    // write texture coordinates
    for (int i = 0; i < textureCoords.size(); i++) {
        std::string vt = std::string("vt") + std::string(" ") + convertToString(float(textureCoords[i].position.x)) + " " + convertToString(float(textureCoords[i].position.y)) + " \n";
        objFile << vt;
    }

    // write vertex normals
    for (int i = 0; i < normals.size(); i++) {
        std::string vn = std::string("vn") + std::string(" ") + convertToString(float(normals[i].position.x)) + " " + convertToString(float(normals[i].position.y)) + " " +
                        convertToString(float(normals[i].position.z)) + "\n";
        objFile << vn;
    }
   
    objFile << textBeforeFaces;

    // write faces
    for (int i = 0; i < faces.size(); i++) {
        std::string f1 = std::string("f") + std::string(" ") + convertToString(float(faces[i].indexVertex1+1)) + "/" + convertToString(float(faces[i].indexTextureCoord1+1)) + "/" +
                        convertToString(float(faces[i].indexNormal+1)) + " ";
        std::string f2 = convertToString(float(faces[i].indexVertex2+1)) + "/" + convertToString(float(faces[i].indexTextureCoord2+1)) + "/" +
                        convertToString(float(faces[i].indexNormal+1)) + " ";
        std::string f3 = convertToString(float(faces[i].indexVertex3+1)) + "/" + convertToString(float(faces[i].indexTextureCoord3+1)) + "/" +
                        convertToString(float(faces[i].indexNormal+1)) + "\n";
        std::string face = f1 + f2 + f3;
        objFile << face;
    }



    objFile.close();

}

void ObjLoader::readSmplUVRef(std::string reference_obj_path, std::vector<Point<glm::vec3>>& _points, std::vector<TriangleCell>& _faces, std::vector<Point<glm::vec2>>& _texCoords) {
    std::vector<std::string*> _positions;

    std::fstream file_in(reference_obj_path);
    if (!file_in.is_open()) {
        std::cout << "[ObjLoader::loadModel] cannot load obj file\n";
        return;
    }
    //std::cout << "obj_path" << obj_path << "\n";
    char buffer[256];
    while (!file_in.eof()) {
        file_in.getline(buffer, 256);
        _positions.push_back(new std::string(buffer));
    }

    unsigned int vertexIndex = 0;
    unsigned int normalIndex = 0;
    unsigned int triangleIndex = 0;
    unsigned int textureIndex = 0;
    for (int i = 0; i < _positions.size(); i++) {
        if (_positions[i]->c_str()[0] == '#') {
            continue;
        } else if (_positions[i]->c_str()[0] == 'v' && _positions[i]->c_str()[1] == 't') {
            glm::vec2 texCoord;
            sscanf(_positions[i]->c_str(), "vt %f %f", &texCoord.x, &texCoord.y);

            _texCoords.push_back(Point(texCoord, textureIndex));
            textureIndex += 1;
        }  else if (_positions[i]->c_str()[0] == 'v' && _positions[i]->c_str()[1] == ' ') {
            glm::vec3 pos;
            sscanf(_positions[i]->c_str(), "v %f %f %f", &pos.x, &pos.y, &pos.z);
            //std::cout << "pos.x: " << pos.x << "\n";
            _points.push_back(Point(pos, vertexIndex));
            vertexIndex += 1;
        } else if (_positions[i]->c_str()[0] == 'f') {
            unsigned int v1,v2,v3, n1, vt1,vt2,vt3;

            sscanf(_positions[i]->c_str(), "f %d/%d/%d %d/%d/%d %d/%d/%d", 
                   &v1,&vt1,&n1, &v2,&vt2,&n1, &v3,&vt3,&n1);
            //std::cout << "v1: " << v1 << ", v2: " << v2 << ", v3: " << v3 << "\n";
            _faces.push_back(TriangleCell(v1-1,v2-1,v3-1,n1-1,triangleIndex,vt1-1,vt2-1,vt3-1));
            triangleIndex += 1;
        }
        
    }

    // cleanup
    for (int i = 0; i < _positions.size(); i++) 
        delete _positions[i];
}

void ObjLoader::loadBasicObj(std::string obj_path, std::vector<Point<glm::vec3>>& _points) {
    std::vector<std::string*> _positions;

    std::fstream file_in(obj_path);
    if (!file_in.is_open()) {
        std::cout << "[ObjLoader::loadModel] cannot load obj file\n";
        return;
    }
    //std::cout << "obj_path" << obj_path << "\n";
    char buffer[256];
    while (!file_in.eof()) {
        file_in.getline(buffer, 256);
        _positions.push_back(new std::string(buffer));
    }

    unsigned int vertexIndex = 0;
    unsigned int normalIndex = 0;
    unsigned int triangleIndex = 0;
    unsigned int textureIndex = 0;
    for (int i = 0; i < _positions.size(); i++) {
        if (_positions[i]->c_str()[0] == '#') {
            continue;
        } else if (_positions[i]->c_str()[0] == 'v' && _positions[i]->c_str()[1] == ' ') {
            glm::vec3 pos;
            sscanf(_positions[i]->c_str(), "v %f %f %f", &pos.x, &pos.y, &pos.z);
            //std::cout << "pos.x: " << pos.x << "\n";
            _points.push_back(Point(pos, vertexIndex));
            vertexIndex += 1;
        } 
        
    }

    // cleanup
    for (int i = 0; i < _positions.size(); i++) 
        delete _positions[i];
}