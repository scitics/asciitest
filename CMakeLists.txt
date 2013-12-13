# -*- coding: utf-8 -*-
#
# file: CMakeLists.txt (asciitest_example)
#
# Copyright 2011 - 2013 scitics GmbH
#

project( asciitest_example )

cmake_minimum_required(VERSION 2.8)

enable_testing()

if(NOT CMAKE_SOURCE_DIR STREQUAL CMAKE_CURRENT_SOURCE_DIR)
    message( FATAL_ERROR "this is the example CMake project made to "
                         "demonstrate how to use asciitest inside a CMake "
                         "environment. In your own project import the "
                         "asciitest folder instead")
endif()

set(ASCIIDOC_DIR "${CMAKE_CURRENT_SOURCE_DIR}/asciitest/CMakeModules/")

if(NOT ASCIIDOC_EXECUTABLE)
    if(NOT ASCIIDOC_DIR)
        message(WARNING "ASCIIDOC_EXECUTABLE not set - we will search for it"
                        "and use the standard location. Set ASCIIDOC_DIR to "
                        "let a preferred (write enabled) installation.")
    endif()

    #[todo] - make use of ASCIIDOC_DIR

    set(CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH} "${CMAKE_CURRENT_SOURCE_DIR}/asciitest/CMakeModules/" )

    find_package(Asciidoc REQUIRED)
endif()

add_subdirectory(asciitest)

file( GLOB_RECURSE ${PROJECT_NAME}_FILES
    README.md
    "${CMAKE_CURRENT_SOURCE_DIR}/*.py"
    "${CMAKE_CURRENT_SOURCE_DIR}/*.txt"
    "${CMAKE_CURRENT_SOURCE_DIR}/*.conf"
)

add_executable(example example.cpp
    ${${PROJECT_NAME}_FILES}
)

add_dependencies(example asciitest)

add_test(generic_cpp_success example)
add_test(generic_cpp_failure example failure)
