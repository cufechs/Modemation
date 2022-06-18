#include "Point.h"
#include <iostream>
#include <glm/glm.hpp>

int main() {

    std::cout << "[Point] included successfully\n";

    Point<glm::vec3> p1(glm::vec3(1,2,3), 0);
    std::cout << "index: " << p1.getIndex() <<"\n";

    return 0;
}
