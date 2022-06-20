#include "BuildSSM.h"


BuildSSM::BuildSSM() {

}

BuildSSM::BuildSSM(const std::string& dir_path) {
    std::cout << "directory: " << dir_path << "\n";
    add_files_to_vec(dir_path, "json", metadata_files);
    add_files_to_vec(dir_path, "obj", meshes_files);
}

BuildSSM::BuildSSM(const std::string& dir_path, const std::string& reference_obj) {
    std::cout << "directory: " << dir_path << "\n";
    add_files_to_vec(dir_path, "obj", meshes_files);

    // read in the reference mesh to get the faces and texture coordinates
    ObjLoader::readSmplUVRef(reference_obj, referenceObj.points, referenceObj.triangleCells, referenceObj.textureCoords);
}

void BuildSSM::add_files_to_vec(const std::string& dir, const std::string& delim, std::vector<std::string>& v) {
    for (const auto& file: std::filesystem::directory_iterator(dir)) {
        std::string filename = file.path().u8string();
        std::size_t pos = filename.find(delim);
        if (pos >= 0 && pos < filename.size()) {
            v.push_back(filename);
        }
    }
}

BuildSSM::~BuildSSM() {
 
}
// file_extension example: .json, .obj
std::string BuildSSM::getNameFromFile(const std::string& filepath, const std::string& file_extension) {
    std::size_t start_index = filepath.find_last_of('/')+1;
    std::size_t last_index = filepath.find(file_extension);
    std::string name = filepath.substr(start_index, last_index-start_index);
    return name;
}

std::string BuildSSM::getCorrespondingMetadataFile(const std::string& mesh_file_path) {
    std::string mesh_filename = getNameFromFile(mesh_file_path, ".obj");

    for (const auto& metadata_file: metadata_files ) {
        std::string metadata_filename = getNameFromFile(metadata_file, ".json");
        if (mesh_filename == metadata_filename) {
            return metadata_file;
        }
    }

    return "";
}

void BuildSSM::createModelsFromFiles() {
    std::cout << "meshes_files.size(): " << meshes_files.size() << "\n";
    for (int i = 0; i < meshes_files.size(); i++) {
        Model m(meshes_files[i]);
        models.push_back(m);
        // search for its corresponding json file 
        std::string metadata_filepath = this->getCorrespondingMetadataFile(meshes_files[i]);
        models[i].setMetadata(metadata_filepath);
    }

    for (int i = 0; i < models.size(); i++) {
        std::cout << models[i].getName() << "   height: " << models[i].getHeight() << "\n";
    }
}

void BuildSSM::createModelsSmpl() {
    std::cout << "number of meshes: " << meshes_files.size() << "\n";
    for (int i = 0; i < meshes_files.size(); i++) {
        Model m(meshes_files[i], referenceObj.triangleCells, referenceObj.textureCoords);
        models.push_back(m);
    }
    std::cout << "[BuildSSM::createModelsSmpl]::done\n";
}

void BuildSSM::createStatsFromMetadata() {
    averageHeight = 0.0;
    averageWeight = 0.0;

    for (const auto& model: models) {
        averageHeight += model.getHeight();
        averageWeight += model.getWeight();
    }

    averageHeight /= models.size();
    averageWeight /= models.size();
}

void BuildSSM::createDeformationFields() {
    
    // assign reference and rest of models
    referenceModel = &models[0];

    for (int i = 1; i < models.size(); i++) {
        std::vector<DeformationField> d;
        for (int j = 0; j < models[i].mesh.points.size(); j++) {
            DeformationField df;
            df.vectorField = models[i].mesh.points[j].position - referenceModel->mesh.points[j].position;
            df.index = models[i].mesh.points[j].index;
            d.push_back(df);
        }
        deformationFields.push_back(d);
    }

}

Model BuildSSM::createMeanModel() {
    
    Mesh meanMesh;
    float meanHeight = 0.0;
    float meanWeight = 0.0;
    std::vector<Point<glm::vec3>> meanPoints;

    glm::vec3 v(0.0f,0.0f,0.0f);
    // initialize positions of meanPoints with zeros
    for (int i = 0; i < models[0].mesh.points.size(); i++) {
        meanPoints.push_back(Point<glm::vec3>(v, models[0].mesh.points[i].index));
    }

    for (int i = 0; i < models.size(); i++) {
        for (int j = 0; j < models[i].mesh.points.size(); j++) {
            meanPoints[j].position += models[i].mesh.points[j].position;
        }
        meanHeight += models[i].getHeight();
        meanWeight += models[i].getWeight();
    }

    meanHeight /= float(models.size());
    meanWeight /= float(models.size());

    // divide by size to get the mean points
    for (int i = 0; i < meanPoints.size(); i++) {
        meanPoints[i].position /= meanPoints.size();
    }

    meanMesh.setMesh(meanPoints, models[0].mesh.triangleCells);

    Model meanModel(meanMesh, meanWeight, meanHeight);
    return meanModel;
}

void BuildSSM::computeGPA() {

    for (int i = 0; i < models.size(); i++) {
        models[i].mesh.deTranslate();
        models[i].mesh.deScale();
    }
    
    for (int i = 1; i < models.size(); i++) {
        Alignment::ICP(models[i], models[0]);
    }
    
}

void BuildSSM::createPCA() {

    pcaModel = new PCA(deformationFields);
    pcaModel->computeEig();
   
}




Mesh BuildSSM::vectorXfToMesh(Eigen::VectorXf vec) {

    Mesh newMesh;
    std::vector<Point<glm::vec3>> points;
    // triangle cells vertices are the same across all models
    std::vector<TriangleCell> triangleCells = models[0].mesh.triangleCells;

    unsigned int pointIndex = 0;
    for (int i = 0; i < vec.size(); i+=3) {
        float x = vec[i];
        float y = vec[i+1];
        float z = vec[i+2];
        Point<glm::vec3> point(glm::vec3(x,y,z), pointIndex);
        pointIndex++;
        
        points.push_back(point);
    }

    newMesh.setMesh(points, triangleCells);
    newMesh.textureCoords = models[0].mesh.textureCoords;
    // newMesh.computeNormals();
    return newMesh;
}

Eigen::VectorXf BuildSSM::MeshToVectorXf(Mesh m) {
    
    Eigen::VectorXf vec(3*m.points.size());

    int k = 0;
    for (int i = 0; i < m.points.size(); i++) {
        vec[k] = m.points[i].position.x;
        vec[k+1] = m.points[i].position.y;
        vec[k+2] = m.points[i].position.z;
        k += 3;
    }

    return vec;
}

Mesh BuildSSM::sampleSSM(Eigen::VectorXf coefficients) {
    // multiply the coefficients by the eigen vectors matrix
    Eigen::VectorXf projection = pcaModel->getProjection(coefficients);

    //std::cout << "projection.sum(): " << projection.sum() << "\n";
    Model meanModel = createMeanModel();

    Eigen::VectorXf meanVector = MeshToVectorXf(meanModel.mesh);

    Eigen::VectorXf sample = meanVector + projection;

    Mesh sampledMesh = vectorXfToMesh(sample);
    sampledMesh.textureCoords = models[0].mesh.textureCoords;
    sampledMesh.pointIds = models[0].mesh.pointIds;
    return sampledMesh;

}

Mesh BuildSSM::sampleSSMSmpl(Eigen::VectorXf coefficients) {
    // multiply the coefficients by the eigen vectors matrix
    Eigen::VectorXf projection = pcaModel->getProjection(coefficients);

    Model meanModel = createMeanModel();

    Eigen::VectorXf meanVector = MeshToVectorXf(meanModel.mesh);

    Eigen::VectorXf sample = meanVector + projection;

    Mesh sampledMesh = vectorXfToMesh(sample);
    sampledMesh.textureCoords = referenceObj.textureCoords;
    sampledMesh.triangleCells = referenceObj.triangleCells;
    sampledMesh.pointIds = models[0].mesh.pointIds;
    return sampledMesh;

}


void BuildSSM::readIdsIndicesLandmarks(const std::string& json_path) {
    std::ifstream json_file(json_path);
    // read as json file
    json_file >> this->idsIndicesJson;
    json_file.close();

    std::cout << "[BuildSSM::readIdsIndicesLandmarks]::idsIndicesJson.size(): " << idsIndicesJson.size() << "\n";
}

void BuildSSM::saveLandmarks(std::string json_path, Mesh m) {
    
    nlohmann::json newLmsJson;
    int k = 0;
    for (nlohmann::json::iterator it = idsIndicesJson.begin(); it != idsIndicesJson.end(); ++it) {
        // get id and index from idsIndicesJson
        std::string id = (*it)["id"];
        unsigned int index = (*it)["index"];
        
        Point<glm::vec3> point = m.getPointAtIndex(index);

        // save in newLmsJson
        newLmsJson[k]["id"] = id;
        newLmsJson[k]["coordinates"] = {point.position.x, point.position.y, point.position.z};
        k++;
    }
    std::ofstream writeJson(json_path);
    writeJson << std::setw(4) << newLmsJson << std::endl;
    std::cout << "[BuildSSM::saveLandmarks]::saved landmarks\n";
}

// void BuildSSM::savePCAModel(const std::string& model_path) {
    
//     std::cout << "saving pca model\n";
//     const H5std_string FILE_NAME(model_path);
//     const H5std_string DATASET_NAME1("/model/mean");
//     const H5std_string DATASET_NAME2("/model/noiseVariance");
//     const H5std_string DATASET_NAME3("/model/pcaBasis");
//     const H5std_string DATASET_NAME4("/model/pcaVariance");

//     Model mean = createMeanModel();
//     std::cout << "created mean model\n";
//     Eigen::VectorXf meanVector = MeshToVectorXf(mean.mesh);
//     std::cout << "created mean vector\n";
//     Eigen::MatrixXf eigenVectors = pcaModel->getEigenVectors();
//     std::cout << "created eigenVectors\n";
//     Eigen::VectorXf eigenValues = pcaModel->getEigenValues();
//     std::cout << "created eigenValues\n";

//     const int DIM_MEAN = 3*models[0].mesh.points.size();
//     //const int DIM_MEAN = 3*6890;
//     const int DIM_NOISE_VARIANCE = 1;
//     const int rowsPCA = models[0].mesh.points.size()*3;
//     const int colsPCA = models.size() - 1;

//     float *_mean_data = new float[DIM_MEAN];
//     float *_noiseVariance = new float[DIM_NOISE_VARIANCE];
//     float *_pcaBasis = new float[rowsPCA*colsPCA];
//     float *_pcaVariance = new float[colsPCA];
    

//     try {
//         // Turn off the auto-printing when failure occurs so that we can
//         // handle the errors appropriately
//         Exception::dontPrint();

//         // 1. Create a new file using the default property lists.
//         H5File file(FILE_NAME, H5F_ACC_TRUNC);

//         // 2. Create Groups
//         Group groupModel(file.createGroup("/model"));

//         // 3. Create Data
//         for (int i = 0; i < DIM_MEAN; i++){
//             _mean_data[i] = meanVector[i];
//         }
//         _noiseVariance[0] = 0.0;
//         std::cout << "[BuildSSM::savePCAModel]::mean_data saved\n";

//         for (int i = 0; i < rowsPCA; i++) {
//             for (int j = 0; j < colsPCA; j++) {
//                 _pcaBasis[i*colsPCA + j] = eigenVectors(i,j);
//             }
//         }
//         std::cout << "[BuildSSM::savePCAModel]::pcaBasis saved\n";

//         for (int i = 0; i < colsPCA; i++) {
//             _pcaVariance[i] = eigenValues[i];
//         }
//         std::cout << "[BuildSSM::savePCAModel]::pcaVariance saved\n";

//         // 4. Create dataspace for mean
//         hsize_t dimsMean[1]; // dataset dimensions
//         dimsMean[0]              = DIM_MEAN;
//         DataSpace *dataspace = new DataSpace(1, dimsMean);
//         // 5. Create the dataset in group
//         DataSet *dataset = new DataSet(file.createDataSet(DATASET_NAME1, PredType::NATIVE_FLOAT, *dataspace));
//         // Write the data to the dataset using default memory space, file
//         // space, and transfer properties.
//         dataset->write(_mean_data, PredType::NATIVE_FLOAT);
//         // Close the current dataset and data space.
//         delete dataset;
//         delete dataspace;

//         // noiseVariance
//         hsize_t dimsNoiseVariance[1];
//         dimsNoiseVariance[0]   = 1;
//         dataspace = new DataSpace(1, dimsNoiseVariance);
//         dataset = new DataSet(groupModel.createDataSet(DATASET_NAME2, PredType::NATIVE_FLOAT, *dataspace));
//         dataset->write(_noiseVariance, PredType::NATIVE_FLOAT);
//         delete dataset;
//         delete dataspace;

//         // pcaVariance
//         hsize_t dimsPCAVariance[1];
//         dimsPCAVariance[0]   = colsPCA;
//         dataspace = new DataSpace(1, dimsPCAVariance);
//         dataset = new DataSet(groupModel.createDataSet(DATASET_NAME4, PredType::NATIVE_FLOAT, *dataspace));
//         dataset->write(_pcaVariance, PredType::NATIVE_FLOAT);
//         delete dataset;
//         delete dataspace;

//         // pcaBasis
//         hsize_t dimsPCABasis[2];
//         dimsPCABasis[0]   = rowsPCA;
//         dimsPCABasis[1]   = colsPCA;
//         dataspace = new DataSpace(2, dimsPCABasis);
//         dataset = new DataSet(groupModel.createDataSet(DATASET_NAME3, PredType::NATIVE_FLOAT, *dataspace));
//         dataset->write(_pcaBasis, PredType::NATIVE_FLOAT);
//         delete dataset;
//         delete dataspace;

//         // cleanup
//         delete [] _mean_data;
//         delete [] _noiseVariance;
//         delete [] _pcaVariance;
//         delete[] _pcaBasis;

//         groupModel.close();

//     } // end of try block

//     // catch failure caused by the H5File operations
//     catch (FileIException error) {
//         error.printErrorStack();
//         return;
//     }

//     // catch failure caused by the DataSet operations
//     catch (DataSetIException error) {
//         error.printErrorStack();
//         return;
//     }

//     // catch failure caused by the DataSpace operations
//     catch (DataSpaceIException error) {
//         error.printErrorStack();
//         return;
//     }

// }

// void BuildSSM::loadPCAModel(const std::string& model_path, const std::string& reference_obj_path) {

//     // 1. read and save reference mesh from reference_obj_path
//     std::vector<TriangleCell> cells;
//     ObjLoader::loadObj(reference_obj_path, referenceMesh.points, referenceMesh.pointIds, referenceMesh.triangleCells, referenceMesh.normals, referenceMesh.textureCoords);

//     const H5std_string FILE_NAME(model_path);
//     const H5std_string MEAN_DATASET_NAME("/model/mean");
//     const H5std_string PCA_BASIS_DATASET_NAME("/model/pcaBasis");
//     const int          DIM0 = referenceMesh.points.size()*3; // dataset dimensions
//     //const int          DIM1 = 79;
//     //const int          DIM1 = 299;
//     const int          DIM1 = 629;
//     const int RANK = 2;

//     Eigen::VectorXf meanVector(DIM0);

//     float *_mean_data = new float[DIM0];
//     float *_eigenVectors = new float[DIM0*DIM1];
    
//     pcaBasis = Eigen::MatrixXf(DIM0, DIM1);

//     try {
//         // Turn off the auto-printing when failure occurs so that we can
//         // handle the errors appropriately
//         Exception::dontPrint();

//         // Open an existing file and dataset.
//         H5File  file(FILE_NAME, H5F_ACC_RDONLY);
//         DataSet dataset = file.openDataSet(MEAN_DATASET_NAME);
    

//         // Write the data to the dataset using default memory space, file
//         // space, and transfer properties.
//         dataset.read(_mean_data, PredType::NATIVE_FLOAT);
//         std::cout << "[BuildSSM::loadPCAModel]::mean data loaded successfully\n";

//         // read mean data
//         for (int i = 0; i < DIM0; i++) {
//             meanVector[i] = _mean_data[i];
//         }
        
//         meanMesh = vectorXfToMesh_w_reference(meanVector);

//         dataset = file.openDataSet(PCA_BASIS_DATASET_NAME);
//         std::cout << "[BuildSSM::loadPCAModel]::pca basis loaded successfully\n";
 
//         dataset.read(_eigenVectors, PredType::NATIVE_FLOAT);
//         std::cout << "[BuildSSM::loadPCAModel]::pca basis saved successfully\n";

//         for (int i = 0; i < DIM0; i++) {
//             for (int j = 0; j < DIM1; j++) {
//                 pcaBasis(i,j) = _eigenVectors[i*DIM1 + j];
//             }
//         }

//         // cleanup
//         delete [] _mean_data;
//         delete[] _eigenVectors;

//     } // end of try block

//     // catch failure caused by the H5File operations
//     catch (FileIException error) {
//         error.printErrorStack();
//         return;
//     }

//     // catch failure caused by the DataSet operations
//     catch (DataSetIException error) {
//         error.printErrorStack();
//         return;
//     }

//     std::cout << "[BuildSSM::loadPCAModel]::pcaModel loading done.\n";
// }


// void BuildSSM::loadPCAModelSmpl(const std::string& model_path, const std::string& reference_obj_path) {

//     std::vector<TriangleCell> cells;
//     ObjLoader::readSmplUVRef(reference_obj_path, referenceMesh.points,  referenceMesh.triangleCells, referenceMesh.textureCoords);

//     const H5std_string FILE_NAME(model_path);
//     const H5std_string MEAN_DATASET_NAME("/model/mean");
//     const H5std_string PCA_BASIS_DATASET_NAME("/model/pcaBasis");
//     //const int          DIM0 = 31425; // dataset dimensions
//     const int          DIM0 = referenceMesh.points.size()*3; // dataset dimensions
//     //const int          DIM1 = 79;
//     //const int          DIM1 = 299;
//     const int          DIM1 = 629;
//     const int RANK = 2;


//     Eigen::VectorXf meanVector(DIM0);

//     float *_mean_data = new float[DIM0];
//     float *_eigenVectors = new float[DIM0*DIM1];
    
//     pcaBasis = Eigen::MatrixXf(DIM0, DIM1);

//     try {
//         // Turn off the auto-printing when failure occurs so that we can
//         // handle the errors appropriately
//         Exception::dontPrint();

//         // Open an existing file and dataset.
//         H5File  file(FILE_NAME, H5F_ACC_RDONLY);
//         DataSet dataset = file.openDataSet(MEAN_DATASET_NAME);
    

//         // Write the data to the dataset using default memory space, file
//         // space, and transfer properties.
//         dataset.read(_mean_data, PredType::NATIVE_FLOAT);

//         // read mean data
//         for (int i = 0; i < DIM0; i++) {
//             meanVector[i] = _mean_data[i];
//         }
//         meanMesh = vectorXfToMesh_w_reference(meanVector);

//         dataset = file.openDataSet(PCA_BASIS_DATASET_NAME);
//         std::cout << "[BuildSSM::loadPCAModelSmpl]::loaded pca basis\n";
        
//         dataset.read(_eigenVectors, PredType::NATIVE_FLOAT);
    

//         for (int i = 0; i < DIM0; i++) {
//             for (int j = 0; j < DIM1; j++) {
//                 pcaBasis(i,j) = _eigenVectors[i*DIM1 + j];
//             }
//         }


//         // cleanup
//         delete [] _mean_data;
//         //for (int i = 0; i < DIM0; i++) delete[] _eigenVectors[i];
//         delete[] _eigenVectors;

//     } // end of try block

//     // catch failure caused by the H5File operations
//     catch (FileIException error) {
//         error.printErrorStack();
//         return;
//     }

//     // catch failure caused by the DataSet operations
//     catch (DataSetIException error) {
//         error.printErrorStack();
//         return;
//     }

//     std::cout << "[BuildSSM::loadPCAModelSmpl]::pcaModel loading done\n";
// }

Mesh BuildSSM::vectorXfToMesh_w_reference(Eigen::VectorXf vec) {
    Mesh newMesh;
    std::vector<Point<glm::vec3>> points;
    // triangle cells vertices are the same across all models
    std::vector<TriangleCell> triangleCells = referenceMesh.triangleCells;

    unsigned int pointIndex = 0;
    for (int i = 0; i < vec.size(); i+=3) {
        float x = vec[i];
        float y = vec[i+1];
        float z = vec[i+2];
        Point<glm::vec3> point(glm::vec3(x,y,z), pointIndex);
        pointIndex++;
        
        points.push_back(point);
    }

    newMesh.setMesh(points, triangleCells);
    newMesh.textureCoords = referenceMesh.textureCoords;
    // newMesh.computeNormals();
    return newMesh;
}

Mesh BuildSSM::instance(Eigen::VectorXf coefficients) {
    Eigen::VectorXf projection = this->pcaBasis.block(0,0,31425,7) * coefficients;
    //Eigen::VectorXf projection = this->pcaBasis.block(0,0,6890*3,10) * coefficients;
 
    Eigen::VectorXf meanVector = MeshToVectorXf(meanMesh);
    Eigen::VectorXf sample = meanVector + projection;
    
    Mesh sampledMesh = vectorXfToMesh_w_reference(sample);
    sampledMesh.textureCoords = referenceMesh.textureCoords;
    sampledMesh.pointIds = referenceMesh.pointIds;
    
    sampledMesh.triangleCells = referenceMesh.triangleCells;
    
    sampledMesh.computeNormals();
    
    return sampledMesh;
}

Mesh BuildSSM::instanceNoNormals(Eigen::VectorXf coefficients) {
    ////Eigen::VectorXf projection = this->pcaBasis.block(0,0,31425,299) * coefficients;
    Eigen::VectorXf projection = this->pcaBasis.block(0,0,31425,7) * coefficients;
    //Eigen::VectorXf projection = this->pcaBasis.block(0,0,6890*3,10) * coefficients;


    Eigen::VectorXf meanVector = MeshToVectorXf(meanMesh);
    Eigen::VectorXf sample = meanVector + projection;
    
    Mesh sampledMesh = vectorXfToMesh_w_reference(sample);
    sampledMesh.textureCoords = referenceMesh.textureCoords;
    sampledMesh.pointIds = referenceMesh.pointIds;
    
    return sampledMesh;
}

nlohmann::json BuildSSM::getIdsIndicesJson() const {
    return idsIndicesJson;
}

std::string BuildSSM::floatToStr (const float & t)
{
  std::ostringstream os;
  os << t;
  return os.str();
}

void BuildSSM::savePCAModel_CSV(const std::string& model_path, const std::string& mean_path) {
    std::ofstream fileMean(mean_path);

    std::cout << "[BuildSSM::savePCAModel_CSV]::starting saveing the model...\n";
    Model mean = createMeanModel();
    std::cout << "[BuildSSM::savePCAModel_CSV]::created mean model\n";
    Eigen::VectorXf meanVector = MeshToVectorXf(mean.mesh);
    std::cout << "[BuildSSM::savePCAModel_CSV]::created mean vector\n";
    Eigen::MatrixXf eigenVectors = pcaModel->getEigenVectors();
    std::cout << "[BuildSSM::savePCAModel_CSV]::created eigenVectors\n";

    const int DIM_MEAN = models[0].mesh.points.size() * 3;
    const int DIM_NOISE_VARIANCE = 1;
    const int rowsPCA = models[0].mesh.points.size() * 3;
    const int colsPCA = models.size() - 1;

    std::string row = "";
    for (int i = 0; i < DIM_MEAN; i++) {
        row += floatToStr(meanVector[i]);
        if (i != DIM_MEAN-1) row += ",";
    }
    fileMean << (row+"\n");
    fileMean.close();
    std::cout << "[BuildSSM::savePCAModel_CSV]::saved mean mesh\n";

    std::ofstream fileModel(model_path);

    for (int i = 0; i < rowsPCA; i++) {
        std::string row = "";
        for (int j = 0; j < colsPCA; j++) {
            row += floatToStr(eigenVectors(i, j));
            if (j != colsPCA - 1) row += ",";
        }
        fileModel << (row + "\n");
    }
    fileModel.close();
    std::cout << "[BuildSSM::savePCAModel_CSV]::saved the pca model\n";
}

void BuildSSM::loadPCAModel_CSV(const std::string& model_path, const std::string& mean_path, const std::string& reference_obj_path) {
    std::vector<TriangleCell> cells;
    ObjLoader::loadObj(reference_obj_path, referenceMesh.points, referenceMesh.pointIds, referenceMesh.triangleCells, referenceMesh.normals, referenceMesh.textureCoords);

    const int          DIM0 = referenceMesh.points.size()*3; // dataset dimensions
    const int          DIM1 = 629;

    Eigen::VectorXf meanVector(DIM0);
    pcaBasis = Eigen::MatrixXf(DIM0, DIM1);

    std::ifstream fileMean(mean_path);
    if (!fileMean.is_open()) {
        std::cout << "Could not open csv file: " << mean_path << "\n"; 
    }

    std::cout << "[BuildSSM::loadPCA_CSV]::starting loading the pca model and mean vector...\n";

    std::string rowMean;
    float numMean;
    int indexMean = 0;

    while (std::getline(fileMean, rowMean)) {
        std::stringstream ss(rowMean);
        while (ss >> numMean) {
            meanVector[indexMean++] = numMean;
            if (ss.peek() == ',') ss.ignore();
        }
    }
    fileMean.close();
    std::cout << "[BuildSSM::loadPCA_CSV]::loaded mean vector\n";

    meanMesh = vectorXfToMesh_w_reference(meanVector);

    std::ifstream fileModel(model_path);
    if (!fileModel.is_open()) {
        std::cout << "Could not open csv file: " << model_path << "\n"; 
    }

    std::string rowModel;
    float numModel;
    int ii = 0;
    int jj = 0;

    while(std::getline(fileModel, rowModel)) {
        std::stringstream ss(rowModel);
        jj = 0;
        while (ss >> numModel) {
            pcaBasis(ii, jj) = numModel;
            if (ss.peek() == ',') ss.ignore();

            jj++;
        }
        ii++;
    }
    fileModel.close();
    std::cout << "[BuildSSM::loadPCA_CSV]::loaded pca basis\n";

    


}