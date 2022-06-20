#ifndef MODEL_H
#define MODEL_H

#include <vector>
#include <string>
#include <fstream>
#include <json/json.hpp>
#include <iostream>
#include <map>
#include <utility>
#include "Mesh.h"
#include "ObjLoader.h"
#include "BodyParameters.h"

class Model {
private: 
    std::string name;
    std::string gender;
    float height;
    float weight;

    float modelHeight;
    std::map<std::string, Point<glm::vec3>> idsPoints;

    std::string getNameFromFile(const std::string& filepath, const std::string& file_extension);
public:
    Mesh mesh;

    Model(const std::string &filename);
    Model(const std::string &filename, std::vector<TriangleCell> faces, std::vector<Point<glm::vec2>> texCoords);
    Model(Mesh mesh);
    Model(Mesh mesh, nlohmann::json idsIndicesJson);
    Model(Mesh mesh, float weight, float height);
    ~Model();

    void loadModel(std::string const &filename);
    void setMetadata(const std::string& filename);
    void setMetadata(float height, float weight);

    float getHeight() const;
    float getWeight() const;
    std::string getGender() const;
    std::string getName() const;
    glm::vec3 getCenterOfMass() const;
    void computeLandmarksPositions(nlohmann::json idsIndicesJson);
    float computeModelHeight();
    float computeArmSpan();
    float computeShoulderWidth();
    float computeParameter(const std::string& start, const std::string& end);

    BodyParameters computeBodyParameters(); // absolute params
    BodyParameters computeBodyRatios(); // with respect to height
    void saveLandmarks(nlohmann::json idsIndicesJson, const std::string& outputPath);
    void saveMesh(const std::string& meshPath);
};



#endif // MODEL_H