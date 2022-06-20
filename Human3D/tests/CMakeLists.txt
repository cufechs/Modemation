cmake_minimum_required(VERSION 3.18)
project( OpencvTest )
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)
find_package( OpenCV REQUIRED )

find_package (Eigen3 3.3 REQUIRED)

find_package(HDF5 REQUIRED CXX HL)

get_filename_component(DIR_ONE_ABOVE ../ ABSOLUTE)

include_directories( 
    ${OpenCV_INCLUDE_DIRS} 
    ${DIR_ONE_ABOVE}/include/
    third_party/glm
    third_party/utils
    third_party/hdf5/1.12.2/include
    )

file(GLOB ALL_SOURCES
    ${DIR_ONE_ABOVE}/src/*.cpp
)
message(STATUS "files: ${ALL_SOURCES}")

add_executable(buildSSM_test buildSSM_test.cpp ${DIR_ONE_ABOVE}/src/Alignment.cpp ${ALL_SOURCES} )
target_link_libraries(buildSSM_test 
    PRIVATE HDF5::HDF5 
    PRIVATE Eigen3::Eigen )


# add_executable(objloader_test objloader_test.cpp ${DIR_ONE_ABOVE}/src/ObjLoader.cpp ${ALL_SOURCES} ${THIRD_PARTY_SOURCES})
# target_link_libraries(objloader_test glfw assimp Eigen3::Eigen)

# add_executable(fileWrite_test fileWrite_test.cpp)

# add_executable(hdf5_test hdf5_test.cpp)
# target_link_libraries(hdf5_test HDF5::HDF5)

# add_executable(hdf5C_test hdf5C_test.cpp)
# target_link_libraries(hdf5C_test HDF5::HDF5)

# add_executable(hdf5Read_test hdf5Read_test.cpp)
# target_link_libraries(hdf5Read_test HDF5::HDF5)

add_executable(readPCAModel_test readPCAModel_test.cpp ${ALL_SOURCES})
target_link_libraries(readPCAModel_test HDF5::HDF5 Eigen3::Eigen)

add_executable(model2_test model2_test.cpp  ${ALL_SOURCES} )
target_link_libraries(model2_test HDF5::HDF5 Eigen3::Eigen)

add_executable(proposals_test proposals_test.cpp  ${ALL_SOURCES} )
target_link_libraries(proposals_test HDF5::HDF5 Eigen3::Eigen)

add_executable(metropolis_test metropolis_test.cpp  ${ALL_SOURCES} )
target_link_libraries(metropolis_test HDF5::HDF5 Eigen3::Eigen)

add_executable(landmarksSmpl_test landmarksSmpl_test.cpp ${ALL_SOURCES})
target_link_libraries(landmarksSmpl_test HDF5::HDF5 Eigen3::Eigen)

add_executable(buildSSMSmpl_test buildSSMSmpl_test.cpp ${DIR_ONE_ABOVE}/src/Alignment.cpp ${ALL_SOURCES} )
target_link_libraries(buildSSMSmpl_test 
    PRIVATE HDF5::HDF5 
    PRIVATE Eigen3::Eigen )

add_executable(readPCAModelSmpl_test readPCAModelSmpl_test.cpp ${ALL_SOURCES})
target_link_libraries(readPCAModelSmpl_test HDF5::HDF5 Eigen3::Eigen)

add_executable(buildSSMSmplx_test buildSSMSmplx_test.cpp ${DIR_ONE_ABOVE}/src/Alignment.cpp ${ALL_SOURCES} )
target_link_libraries(buildSSMSmplx_test 
    PRIVATE HDF5::HDF5 
    PRIVATE Eigen3::Eigen )

add_executable(readPCASmplx_test readPCASmplx_test.cpp ${ALL_SOURCES})
target_link_libraries(readPCASmplx_test HDF5::HDF5 Eigen3::Eigen)

add_executable(landmarks_test landmarks_test.cpp ${ALL_SOURCES})
target_link_libraries(landmarks_test HDF5::HDF5 Eigen3::Eigen)