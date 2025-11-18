cmake_minimum_required(VERSION 3.11)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

include(FetchContent)
FetchContent_Declare(
    pybind11
    GIT_REPOSITORY https://github.com/pybind/pybind11
    GIT_SHALLOW TRUE
)
FetchContent_MakeAvailable(pybind11)

file(GLOB_RECURSE sources
    "./*.hpp"
    "./*.cpp"
)

pybind11_add_module(m_tree ${sources})
target_link_libraries(m_tree PRIVATE m_tree-lib)