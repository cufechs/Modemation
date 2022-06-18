#ifndef DEFORMATIONFIELD_H
#define DEFORMATIONFIELD_H

#include <glm/glm.hpp>

struct DeformationField {
    glm::vec3 vectorField;
    unsigned int index;
};

#endif // DEFORMATIONFIELD_H