cmake_minimum_required(VERSION 3.18)
project( human3d )

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)


find_package (Eigen3 3.3 REQUIRED)

include_directories( 
    include/
    third_party/glm
    third_party/utils
    )

file(GLOB ALL_SOURCES
    src/*.cpp
)
message(STATUS "files: ${ALL_SOURCES}")

add_executable(fitting apps/fitting.cpp  ${ALL_SOURCES} )
target_link_libraries(fitting  Eigen3::Eigen)

add_executable(buildShapeModel apps/buildShapeModel.cpp  ${ALL_SOURCES} )
target_link_libraries(buildShapeModel  Eigen3::Eigen)
