#include "Point.h"


template<class T> 
Point<T>::Point(T vec, unsigned int index) {
    this->position = vec;
    this->index = index;
}

template<class T> 
T Point<T>::getPosition() const {
    return position;
}

template<class T> 
unsigned int Point<T>::getIndex() const {
    return index;
}

template Point<glm::vec3>::Point(glm::vec3 vec, unsigned int index);
template Point<glm::vec2>::Point(glm::vec2 vec, unsigned int index);
template glm::vec3 Point<glm::vec3>::getPosition() const;
template unsigned int Point<glm::vec3>::getIndex() const;
template unsigned int Point<glm::vec2>::getIndex() const;