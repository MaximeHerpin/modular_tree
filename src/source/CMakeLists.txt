cmake_minimum_required(VERSION 3.11)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} --std=c++11 -O3 -fPIC")

include(FetchContent)

FetchContent_Declare(
    Eigen
    GIT_REPOSITORY https://gitlab.com/libeigen/eigen.git
    GIT_SHALLOW TRUE
)
FetchContent_MakeAvailable(Eigen)

file(GLOB_RECURSE sources
    "./*.hpp"
    "./*.cpp"
)

add_library(m_tree-lib STATIC ${sources})
target_include_directories(m_tree-lib PUBLIC ${PROJECT_SOURCE_DIR})
target_link_libraries(m_tree-lib PUBLIC Eigen3::Eigen)

source_group(TREE ${CMAKE_CURRENT_SOURCE_DIR} FILES ${sources})