cmake_minimum_required(VERSION 2.8.12)
# set(CMAKE_TOOLCHAIN_FILE D:/Cpp/vcpkg/scripts/buildsystems/vcpkg.cmake CACHE STRING "")
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