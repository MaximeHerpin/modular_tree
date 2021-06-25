cmake_minimum_required(VERSION 2.8.12)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

set(CMAKE_TOOLCHAIN_FILE ../dependencies/vcpkg/scripts/buildsystems/vcpkg.cmake CACHE STRING "")


file(GLOB_RECURSE sources
    "./*.hpp"
    "./*.cpp"
)

add_executable(m_tree_tests ${sources})

add_test(NAME m_tree_tests COMMAND m_tree_tests)

target_link_libraries(m_tree_tests PRIVATE m_tree-lib)