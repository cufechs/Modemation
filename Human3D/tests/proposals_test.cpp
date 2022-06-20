#include "GaussianProposal.h"
#include <iostream>

void printVec(std::vector<float> v) {
    for (int i = 0; i < v.size(); i++) {
        std::cout << v[i] << " ";
    }
    std::cout << "\n";
}

int main () {

    // std::cout << "GaussianProposal included successfully\n";

    // GaussianProposal gauss(0.1);
    // std::vector<float> v{1,2,3,4,5};

    // std::vector<float> proposed = gauss.propose(v);

    // std::cout << "proposed params: ";
    // printVec(proposed);

    return 0;
}