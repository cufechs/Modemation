#include <iostream>
//#include <h5cpp/hdf5.hpp>
// #include "H5Cpp.h"

#include <string>

//#include "hdf5.h"
#include "H5Cpp.h"
using namespace H5;

const H5std_string DATASET_NAME1("/Model/mean_data");
const H5std_string DATASET_NAME2("/ObjStructure/triangles");
const int          RANK   = 2;
const int          D1DIM1 = 2;
const int          D1DIM2 = 3;
const int          D2DIM1 = 2;
const int          D2DIM2 = 10;
const int          NX   = 4; // dataset dimensions
const int          NY   = 6;

int main() {
    std::string path = "/Users/abdelrahmanabdelghany/Documents/college/semester10/GP/Human3D/tests/h5File_test2.h5";
    const H5std_string FILE_NAME(path);
    int model_data[D1DIM1][D1DIM2], triangles[NY]; // data buffers
    int i, j;
    int *mean_data = new int[5*10];
    //int **mean_data = new int*[5];
    //for (int i = 0; i < 5; i++) mean_data[i] = new int[10];
    // Try block to detect exceptions raised by any of the calls inside it
    try {
        // Turn off the auto-printing when failure occurs so that we can
        // handle the errors appropriately
        Exception::dontPrint();

        // 1. Create a new file using the default property lists.
        H5File file(FILE_NAME, H5F_ACC_TRUNC);

        // 2. Create Groups
        Group groupModel(file.createGroup("/Model"));
        Group groupObjStructure(file.createGroup("/ObjStructure"));

        // 3. Create Model Data
        for (i = 0; i < D1DIM1; i++)
            for (j = 0; j < D1DIM2; j++)
                model_data[i][j] = j + 1;

        // 4. Create dataspace for model_data
        hsize_t dims[RANK]; // dataset dimensions
        dims[0]              = 5;
        dims[1]              = 10;
        DataSpace *dataspace = new DataSpace(RANK, dims);

        // 5. Create the dataset in group
        DataSet *dataset = new DataSet(file.createDataSet(DATASET_NAME1, PredType::STD_I32BE, *dataspace));
        
        int k = 0;
        for (int i = 0; i < 5; i++) {
            for(int j = 0; j < 10; j++) {
                mean_data[i*10+j] = k;
                k++;
                //std::cout << "mean_data["<<i<<"]["<<j<<"]: " << mean_data[i][j] << "\n";
            }
        }

        // Write the data to the dataset using default memory space, file
        // space, and transfer properties.
        dataset->write(mean_data, PredType::NATIVE_INT);

        // Close the current dataset and data space.
        delete dataset;
        delete dataspace;

        //for (int i = 0; i < 5; i++)
            //delete[] mean_data[i];
        delete[] mean_data;

        // // Create the data space for the second dataset.
        // hsize_t dims2[1];
        // dims2[0]   = NY;
        // dataspace = new DataSpace(1, dims2);

        // for (i = 0; i < NY; i++) {
        //     triangles[i]= i+100;
        // }

        // // create the second dataset in groupObjStructure
        // dataset = new DataSet(groupObjStructure.createDataSet(DATASET_NAME2, PredType::STD_I32BE, *dataspace));
        // dataset->write(triangles, PredType::NATIVE_INT);

        // // Close all objects.
        // delete dataspace;
        // delete dataset;
        groupModel.close();
        groupObjStructure.close();

    } // end of try block

    // catch failure caused by the H5File operations
    catch (FileIException error) {
        error.printErrorStack();
        return -1;
    }

    // catch failure caused by the DataSet operations
    catch (DataSetIException error) {
        error.printErrorStack();
        return -1;
    }

    // catch failure caused by the DataSpace operations
    catch (DataSpaceIException error) {
        error.printErrorStack();
        return -1;
    }

    std::cout << "hdf5 test done\n";
    return 0;
}