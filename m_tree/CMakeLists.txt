cmake_minimum_required(VERSION 2.8.12)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)


set(CMAKE_TOOLCHAIN_FILE ./dependencies/vcpkg/scripts/buildsystems/vcpkg.cmake)

set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY ${CMAKE_SOURCE_DIR}/binaries)
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${CMAKE_SOURCE_DIR}/binaries)
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_SOURCE_DIR}/binaries)

project(m_tree)


add_subdirectory(./source)
add_subdirectory(./python_bindings)

