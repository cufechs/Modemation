#ifndef MESH_H 
#define MESH_H

#include <vector>
#include <cmath>
#include "Point.h"
#include "TriangleCell.h"
#include <glm/gtx/normal.hpp>

class Mesh {
private:  
    Point<glm::vec3> getPoint(unsigned int index);
public:  


    std::vector<Point<glm::vec3>> points;
    std::vector<unsigned int> pointIds;
    std::vector<TriangleCell> triangleCells;
    std::vector<Point<glm::vec3>> normals;
    std::vector<Point<glm::vec2>> textureCoords;

    Mesh();
    Mesh(std::vector<Point<glm::vec3>> points);
    ~Mesh();

    void setMesh(std::vector<Point<glm::vec3>> points, std::vector<TriangleCell> triangleCells);
    void setMesh(std::vector<Point<glm::vec3>> points);
    Point<glm::vec3> getClosestPoint(glm::vec3 point); // should return a Point instead
    glm::vec3 getCenterOfMass() const;
    float getScale() const;
    void deTranslate(); // makes the mean point of the mesh zeros
    void deScale(); // makes the scale of the mesh = 1
    void computeNormals();
    void updateNormals();
    void scale(float s);

    Point<glm::vec3> getPointAtIndex(unsigned int pointIndex);

};

#endif //MESH_H

