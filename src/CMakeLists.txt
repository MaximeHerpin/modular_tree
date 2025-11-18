cmake_minimum_required(VERSION 3.11)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

set(ADDON_DIRECTORY ${CMAKE_SOURCE_DIR}/../addon)
set(ADDON_LIB_DIRECTORY ${ADDON_DIRECTORY}/lib/$<0:>)  # Strip configuration subdirectory (Debug, etc.)
set(BUILD_DIRECTORY ${CMAKE_SOURCE_DIR}/../build/$<0:>)

set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY ${BUILD_DIRECTORY})
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${ADDON_LIB_DIRECTORY})
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${BUILD_DIRECTORY})

project(m_tree)

add_subdirectory(./source)
add_subdirectory(./python_bindings)
add_subdirectory(./tests)