cmake_minimum_required(VERSION 2.8.12)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

set(CMAKE_TOOLCHAIN_FILE ../dependencies/vcpkg/scripts/buildsystems/vcpkg.cmake CACHE STRING "")

add_subdirectory(../dependencies/pybind11 [EXCLUDE_FROM_ALL])

file(GLOB_RECURSE sources
    "./*.hpp"
    "./*.cpp"
)

pybind11_add_module(m_tree ${sources})
target_link_libraries(m_tree PRIVATE m_tree-lib)