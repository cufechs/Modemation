#include <glm/glm.hpp>
#include <string>
#include <iostream>
#include <vector>
#include <algorithm>
#include <cstdlib>
#include <fstream>
#include <sstream>
#include "Point.h"
#include "TriangleCell.h"


class ObjLoader {
public:  
    static void loadObj(std::string obj_path, std::vector<Point<glm::vec3>>& points, std::vector<unsigned int>& pointIds, std::vector<TriangleCell>& faces, std::vector<Point<glm::vec3>>& normals, std::vector<Point<glm::vec2>>& textureCoords);
    static void saveObj(std::string obj_path, std::vector<Point<glm::vec3>> points, std::vector<unsigned int> pointIds, std::vector<TriangleCell> faces, std::vector<Point<glm::vec3>> normals, std::vector<Point<glm::vec2>> textureCoords);

    /**
     * @brief reads reference uv smpl and sets the faces and texture coordinates to be used by other smpl models
     * 
     * @param reference_obj_path 
     * @param faces 
     * @param textureCoords 
     */
    static void readSmplUVRef(std::string reference_obj_path, std::vector<Point<glm::vec3>>& _points, std::vector<TriangleCell>& _faces, std::vector<Point<glm::vec2>>& _texCoords);

    /**
     * @brief reads smpl generated models
     * 
     * @param obj_path 
     * @param points 
     * @param faces 
     */
    static void loadBasicObj(std::string obj_path, std::vector<Point<glm::vec3>>& _points);

    template <typename T>
    static std::string convertToString(const T& num) { 
        std::ostringstream ss; 
        ss << num; 
        return ss.str(); 
    } 

private:
    static int x;
    static std::vector<Point<glm::vec2>> smplTexCoords;
    static std::vector<TriangleCell> smplFaces;
};