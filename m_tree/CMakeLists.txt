cmake_minimum_required(VERSION 2.8.12)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

set(CMAKE_TOOLCHAIN_FILE ./vcpkg/scripts/buildsystems/vcpkg.cmake CACHE STRING "")
project(m_tree)

find_package(Eigen3 CONFIG REQUIRED)
add_subdirectory(pybind11)

file(GLOB_RECURSE sources
    "./Source/*.hpp"
    "./Source/*.cpp"
)

pybind11_add_module(m_tree ${sources})
target_link_libraries(m_tree PRIVATE Eigen3::Eigen)