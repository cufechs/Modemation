#ifndef POINT_H
#define POINT_H

#include <glm/glm.hpp>

template<class T>
class Point {
private: 
public:
    T position;
    unsigned int index;
    Point(T vec, unsigned int index);
    T getPosition() const;
    unsigned int getIndex() const;
};

#endif // POINT_H