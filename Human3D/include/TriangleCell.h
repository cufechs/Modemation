#ifndef TRIANGLECELL_H
#define TRIANGLECELL_H

class TriangleCell {
public:
    unsigned int indexVertex1;
    unsigned int indexVertex2;
    unsigned int indexVertex3;

    unsigned int indexNormal;

    unsigned int indexTextureCoord1;
    unsigned int indexTextureCoord2;
    unsigned int indexTextureCoord3;

    unsigned int triangleIndex; // face index

    TriangleCell(unsigned int v1, unsigned int v2, unsigned int v3,
                unsigned int n1, unsigned int index,
                unsigned int texCoord1, unsigned int texCoord2, unsigned int texCoord3) : indexVertex1(v1), indexVertex2(v2), 
                    indexVertex3(v3), indexNormal(n1), triangleIndex(index),
                    indexTextureCoord1(texCoord1), indexTextureCoord2(texCoord2), indexTextureCoord3(texCoord3)    {}
};

#endif // TRIANGLECELL_H