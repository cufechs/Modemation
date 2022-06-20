#include <iostream>
//#include <h5cpp/hdf5.hpp>
// #include "H5Cpp.h"

#include <string>

#include "hdf5.h"



int main() {
    std::string path = "/Users/abdelrahmanabdelghany/Documents/college/semester10/GP/Human3D/tests/h5File_test2C.h5";
    
    //hid_t   file_id, dataset_id, dataspace_id; /* identifiers */
    //hsize_t dims[2];
    //herr_t  status;

    /* Create a new file using default properties. */
    //file_id = H5Fcreate(path.c_str(), H5F_ACC_TRUNC, H5P_DEFAULT, H5P_DEFAULT, H5F_ACC_RDWR);

    // /* Create the data space for the dataset. */
    // dims[0]      = 4;
    // dims[1]      = 6;
    // dataspace_id = H5Screate_simple(2, dims, NULL);

    // /* Create the dataset. */
    // dataset_id =
    //     H5Dcreate2(file_id, "/dset", H5T_STD_I32BE, dataspace_id, H5P_DEFAULT, H5P_DEFAULT, H5P_DEFAULT);

    // /* End access to the dataset and release resources used by it. */
    // status = H5Dclose(dataset_id);

    // /* Terminate access to the data space. */
    // status = H5Sclose(dataspace_id);

    // /* Close the file. */
    // status = H5Fclose(file_id);


    // --------------------------
    // read and write to dataset
    // hid_t  file_id, dataset_id; /* identifiers */
    // herr_t status;
    // int    i, j, dset_data[4][6];

    // /* Initialize the dataset. */
    // for (i = 0; i < 4; i++)
    //     for (j = 0; j < 6; j++)
    //         dset_data[i][j] = i * 6 + j + 1;

    // /* Open an existing file. */
    // file_id = H5Fopen(path.c_str(), H5F_ACC_RDWR, H5P_DEFAULT);

    // /* Open an existing dataset. */
    // dataset_id = H5Dopen2(file_id, "/dset", H5P_DEFAULT);

    // /* Write the dataset. */
    // status = H5Dwrite(dataset_id, H5T_NATIVE_INT, H5S_ALL, H5S_ALL, H5P_DEFAULT, dset_data);

    // status = H5Dread(dataset_id, H5T_NATIVE_INT, H5S_ALL, H5S_ALL, H5P_DEFAULT, dset_data);

    // /* Close the dataset. */
    // status = H5Dclose(dataset_id);

    // /* Close the file. */
    // status = H5Fclose(file_id);
    // --------------------------



    // --------------------------
    // create a group

    // hid_t  file_id, group_id; /* identifiers */
    // herr_t status;

    // /* Create a new file using default properties. */
    // file_id = H5Fcreate(path.c_str(), H5F_ACC_TRUNC, H5P_DEFAULT, H5P_DEFAULT);

    // /* Create a group named "/MyGroup" in the file. */
    // group_id = H5Gcreate2(file_id, "/MyGroup", H5P_DEFAULT, H5P_DEFAULT, H5P_DEFAULT);

    // /* Close the group. */
    // status = H5Gclose(group_id);

    // /* Terminate access to the file. */
    // status = H5Fclose(file_id);
    // --------------------------



    // --------------------------
    // Create groups in a file using absolute and relative paths

    hid_t  file_id, group1_id, group2_id, group3_id; /* identifiers */
    herr_t status;

    /* Create a new file using default properties. */
    file_id = H5Fcreate(path.c_str(), H5F_ACC_TRUNC, H5P_DEFAULT, H5P_DEFAULT);

    /* Create group "MyGroup" in the root group using absolute name. */
    group1_id = H5Gcreate2(file_id, "/MyGroup", H5P_DEFAULT, H5P_DEFAULT, H5P_DEFAULT);

    /* Create group "Group_A" in group "MyGroup" using absolute name. */
    group2_id = H5Gcreate2(file_id, "/MyGroup/Group_A", H5P_DEFAULT, H5P_DEFAULT, H5P_DEFAULT);

    /* Create group "Group_B" in group "MyGroup" using relative name. */
    group3_id = H5Gcreate2(group1_id, "Group_B", H5P_DEFAULT, H5P_DEFAULT, H5P_DEFAULT);

    /* Close groups. */
    status = H5Gclose(group1_id);
    status = H5Gclose(group2_id);
    status = H5Gclose(group3_id);

    /* Close the file. */
    status = H5Fclose(file_id);
    // --------------------------




    // --------------------------
    // create datasets in a group

    hid_t    group_id, dataset_id, dataspace_id; /* identifiers */
    hsize_t dims[2];
    int     i, j, dset1_data[3][3], dset2_data[2][10];

    const int rows = 3;
    const int cols = 5;
    //int **mean_data = new int*[rows];
    //int **mean_data;
    //mean_data = (int**)malloc(sizeof(int*)*rows);
    //for(int i = 0; i < rows; i++) mean_data[i] = (int*)malloc(sizeof(int)*cols);
    //for(int i = 0; i < rows; i++) mean_data[i] = new int[cols];
    int *mean_data = new int[rows*cols];


    int k = 0;
    for (int i = 0; i < rows; i++) 
        for(int j = 0; j < cols; j++)
            mean_data[i*cols + j] = k++;

    
    int a = 0;
    /* Initialize the first dataset. */
    for (i = 0; i < 3; i++)
        for (j = 0; j < 3; j++)
            dset1_data[i][j] = a++;//j + 1;

    /* Initialize the second dataset. */
    for (i = 0; i < 2; i++)
        for (j = 0; j < 10; j++)
            dset2_data[i][j] = j + 1;

    /* Open an existing file. */
    file_id = H5Fopen(path.c_str(), H5F_ACC_RDWR, H5P_DEFAULT);

    /* Create the data space for the first dataset. */
    dims[0]      = 3;
    dims[1]      = 3;
    dataspace_id = H5Screate_simple(2, dims, NULL);

    /* Create a dataset in group "MyGroup". */
    dataset_id = H5Dcreate2(file_id, "/MyGroup/dset1", H5T_STD_I32BE, dataspace_id, H5P_DEFAULT, H5P_DEFAULT,
                            H5P_DEFAULT);

    /* Write the first dataset. */
    status = H5Dwrite(dataset_id, H5T_NATIVE_INT, H5S_ALL, H5S_ALL, H5P_DEFAULT, dset1_data);
    std::cout << "status: " << status << "\n";

    /* Close the data space for the first dataset. */
    status = H5Sclose(dataspace_id);

    /* Close the first dataset. */
    status = H5Dclose(dataset_id);

    /* Open an existing group of the specified file. */
    group_id = H5Gopen2(file_id, "/MyGroup/Group_A", H5P_DEFAULT);

    /* Create the data space for the second dataset. */
    dims[0]      = rows;//2;
    dims[1]      = cols;//10;
    dataspace_id = H5Screate_simple(2, dims, NULL);

    /* Create the second dataset in group "Group_A". */
    dataset_id =
        H5Dcreate2(group_id, "dset2", H5T_STD_I32BE, dataspace_id, H5P_DEFAULT, H5P_DEFAULT, H5P_DEFAULT);

    /* Write the second dataset. */
    //status = H5Dwrite(dataset_id, H5T_NATIVE_INT, H5S_ALL, H5S_ALL, H5P_DEFAULT, dset2_data);
    status = H5Dwrite(dataset_id, H5T_NATIVE_INT, H5S_ALL, H5S_ALL, H5P_DEFAULT, mean_data);
    std::cout << "status: " << status << "\n";

    /* Close the data space for the second dataset. */
    status = H5Sclose(dataspace_id);

    /* Close the second dataset */
    status = H5Dclose(dataset_id);

    /* Close the group. */
    status = H5Gclose(group_id);

    /* Close the file. */
    status = H5Fclose(file_id);
    // --------------------------


    //for (int i = 0; i < rows; i++) delete[] mean_data[i];
    delete[] mean_data;

    std::cout << "hdf5C test done\n";
    return 0;
}