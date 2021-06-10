cmake_minimum_required(VERSION 2.8.12)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# set(CMAKE_TOOLCHAIN_FILE ../dependencies/vcpkg/scripts/buildsystems/vcpkg.cmake)

project(m_tree-lib)

find_package(Eigen3 CONFIG REQUIRED)

file(GLOB_RECURSE sources
    "./*.hpp"
    "./*.cpp"
)

add_library(m_tree-lib STATIC ${sources})
target_include_directories(m_tree-lib PUBLIC ${PROJECT_SOURCE_DIR})
target_link_libraries(m_tree-lib PUBLIC Eigen3::Eigen)