#include "Model.h"

Model::Model(const std::string &filename) {
    loadModel(filename);
}

Model::Model(const std::string &filename, std::vector<TriangleCell> faces, std::vector<Point<glm::vec2>> texCoords) {
    ObjLoader::loadBasicObj(filename, mesh.points);
    mesh.triangleCells = faces;
    mesh.textureCoords = texCoords;
    //mesh.computeNormals();
}

Model::Model(Mesh mesh) {
    this->mesh = mesh;
}

Model::Model(Mesh mesh, float weight, float height) {
    this->mesh = mesh;
    this->weight = weight;
    this->height = height;
}

Model::Model(Mesh mesh, nlohmann::json idsIndicesJson) {
    this->mesh = mesh;
    computeLandmarksPositions(idsIndicesJson);
}

void Model::loadModel(const std::string& filename) {
    ObjLoader::loadObj(filename, mesh.points, mesh.pointIds, mesh.triangleCells, mesh.normals, mesh.textureCoords);
}

Model::~Model() {
    
}

// file_extension example: .json, .obj
std::string Model::getNameFromFile(const std::string& filepath, const std::string& file_extension) {
    std::size_t start_index = filepath.find_last_of('/')+1;
    std::size_t last_index = filepath.find(file_extension);
    std::string name = filepath.substr(start_index, last_index-start_index);
    return name;
}

void Model::setMetadata(const std::string& filename) {
    std::ifstream json_file(filename);
    nlohmann::json json;
    json_file >> json;
    json_file.close();

    this->gender = json["gender"];
    this->height = json["height"];
    this->weight = json["weight"];

    std::string modelName = getNameFromFile(filename, ".json");
    this->name = modelName;
}

std::string Model::getGender() const {
    return this->gender;
}

float Model::getHeight() const {
    return this->height;
}

float Model::getWeight() const {
    return this->weight;
}

std::string Model::getName() const {
    return this->name;
}

glm::vec3 Model::getCenterOfMass() const {
    return mesh.getCenterOfMass();
}

void Model::setMetadata(float height, float weight) {
    this->height = height;
    this->weight = weight;
}

void Model::computeLandmarksPositions(nlohmann::json idsIndicesJson) {
    idsPoints.clear();

    for (nlohmann::json::iterator it = idsIndicesJson.begin(); it != idsIndicesJson.end(); ++it) {
        // get id and index from idsIndicesJson
        std::string id = (*it)["id"];
        unsigned int index = (*it)["index"];
        
        Point<glm::vec3> point = mesh.getPointAtIndex(index);
        
        idsPoints.insert(std::make_pair(id, point));
    }

    std::map<std::string, Point<glm::vec3>>::iterator it;
    it = idsPoints.find("nosetip");
    
    //std::cout << "idsPoints[nosetip].position.x: " << it->second.position.x << "\n";
}

float Model::computeModelHeight() {

    std::map<std::string, Point<glm::vec3>>::iterator it;
    
    it = idsPoints.find("head.top");
    glm::vec3 head_top = it->second.position;
    //std::cout << "head_top: (" << head_top.x << ", " << head_top.y << ", " << head_top.z << ")\n";

    it = idsPoints.find("foot.left.bottom.center");
    glm::vec3 foot_bottom = it->second.position;
    //std::cout << "foot_bottom: (" << foot_bottom.x << ", " << foot_bottom.y << ", " << foot_bottom.z << ")\n";

    
    float model_height = sqrt(pow(head_top.x - foot_bottom.x, 2) + pow(head_top.y - foot_bottom.y, 2) + pow(head_top.z - foot_bottom.z, 2));    
    //std::cout << "s: " << s << "\n";
    //float modeHeight = glm::distance(head_top, foot_bottom);
    this->modelHeight = model_height;
    return model_height;
}

float Model::computeArmSpan() {
    std::map<std::string, Point<glm::vec3>>::iterator it;
    
    it = idsPoints.find("fist.right.fist");
    glm::vec3 fist_right = it->second.position;

    it = idsPoints.find("fist.left.fist");
    glm::vec3 fist_left = it->second.position;

    float armSpan = sqrt(pow(fist_right.x - fist_left.x, 2) + pow(fist_right.y - fist_left.y, 2) + pow(fist_right.z - fist_left.z, 2));

    return armSpan;
}

float Model::computeShoulderWidth() {
    std::map<std::string, Point<glm::vec3>>::iterator it;
    
    it = idsPoints.find("shoulder.right.top");
    glm::vec3 shoulder_right = it->second.position;

    it = idsPoints.find("shoulder.left.top");
    glm::vec3 shoulder_left = it->second.position;

    float shoulderWidth = sqrt(pow(shoulder_right.x - shoulder_left.x, 2) + pow(shoulder_right.y - shoulder_left.y, 2) + pow(shoulder_right.z - shoulder_left.z, 2));
    //std::cout << "shoulder: " << glm::distance(shoulder_left, shoulder_right) << "\n";
    return shoulderWidth;
}

float Model::computeParameter(const std::string& start, const std::string& end) {
    std::map<std::string, Point<glm::vec3>>::iterator it;
    
    it = idsPoints.find(start);
    glm::vec3 first = it->second.position;

    it = idsPoints.find(end);
    glm::vec3 second = it->second.position;

    float param = sqrt(pow(first.x - second.x, 2) + pow(first.y - second.y, 2) + pow(first.z - second.z, 2));
    
    return param;
}

BodyParameters Model::computeBodyParameters() {
    BodyParameters params;

    params.armSpan = computeArmSpan();
    params.shoulderWidth = computeShoulderWidth();
    params.height = computeModelHeight();

    return params;
}

BodyParameters Model::computeBodyRatios() {
    BodyParameters params;

    params.height = computeModelHeight();
    params.shoulderWidth = computeShoulderWidth();
    params.armSpan = computeArmSpan();
    params.stomachWidth = computeParameter("belly.right", "belly.left");
    params.chestWidth = computeParameter("chest.right", "chest.left");
    params.legHeight = computeParameter("waist.right", "foot.right.bottom.center");
    //params.neckLength = computeParameter("chin", "neckstart.front.center");
    params.neckLength = computeParameter("neck.right.upper", "neck.right.lower");
    params.headWidth = computeParameter("head.right", "head.left");
    params.headIntoLength = computeParameter("nosetip", "head.back");
    params.thighRighWidth = computeParameter("thigh.right.outer", "thigh.right.inner");

    params.shoulderWidthRatio = params.shoulderWidth / params.height;
    params.armSpanRatio = params.armSpan / params.height;
    params.stomachWidthRatio = params.stomachWidth / params.height;
    params.chestWidthRatio = params.chestWidth / params.height;
    params.legHeightRatio = params.legHeight / params.height;
    params.neckLengthRatio = params.neckLength / params.height;
    params.headWidthRatio = params.headWidth / params.height;
    params.headIntoLengthRatio = params.headIntoLength / params.height;
    params.thighRightWidthRatio = params.thighRighWidth / params.height;

    return params;

}

void Model::saveLandmarks(nlohmann::json idsIndicesJson, const std::string& outputPath) {
    nlohmann::json newLmsJson;
    int k = 0;
    for (nlohmann::json::iterator it = idsIndicesJson.begin(); it != idsIndicesJson.end(); ++it) {
        // get id and index from idsIndicesJson
        std::string id = (*it)["id"];
        unsigned int index = (*it)["index"];
        //std::cout << "index: " << index << "\n";
        Point<glm::vec3> point = this->mesh.getPointAtIndex(index);

        // save in newLmsJson
        newLmsJson[k]["id"] = id;
        newLmsJson[k]["coordinates"] = {point.position.x, point.position.y, point.position.z};
        k++;
    }
    std::ofstream writeJson(outputPath);
    //writeJson << std::setw(4) << newLmsJson << std::endl;
    writeJson << newLmsJson << std::endl;
    std::cout << "[Model::saveLandmarks]::saved landmarks from model successfully\n";
}

void Model::saveMesh(const std::string& meshPath) {
    ObjLoader::saveObj(meshPath,
         this->mesh.points, this->mesh.pointIds, this->mesh.triangleCells,
         this->mesh.normals, this->mesh.textureCoords);
}