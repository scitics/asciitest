# -*- coding: utf-8 -*-
#
# file: CMakeLists.txt (asciitest_example)
#
# (C) Copyright 2011 - 2014 scitics GmbH
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or imp#lied.
# See the License for the specific language governing permissions and
# limitations under the License.
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

set(CONFIG_ASCIIDOC_ALTERNATIVE_DIR "" CACHE PATH "location of asciidoc installation")

message( STATUS "ASCIIDOC_EXECUTABLE: ${ASCIIDOC_EXECUTABLE}")

if(NOT ASCIIDOC_EXECUTABLE)
    if(NOT IS_DIRECTORY "${CONFIG_ASCIIDOC_ALTERNATIVE_DIR}")
 
        message(WARNING "ASCIIDOC_EXECUTABLE not set - we will search for it"
                        "and use the standard location. Set ASCIIDOC_DIR to "
                        "set a preferred (write enabled) installation.")
    endif()

    #[todo] - make use of CONFIG_ASCIIDOC_ALTERNATIVE_DIR

    set(CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH} "${CMAKE_CURRENT_SOURCE_DIR}/asciitest/CMakeModules/" )

    find_package(Asciidoc REQUIRED)
endif()

option(CONFIG_HAVE_ASCIIDOC "let asciidoc with asciitest create docs and tests" ON)
message( STATUS "CONFIG_HAVE_ASCIIDOC: ${CONFIG_HAVE_ASCIIDOC}")
if(CONFIG_HAVE_ASCIIDOC)
    set(CONFIG_ASCIITEST_DOC_PATTERN "EXAMPLE-DOC*.txt" CACHE STRING "how are asciitest documentation files named?")
    add_subdirectory(asciitest)
    run_env_add_variable("PYTHONPATH" "${CMAKE_BINARY_DIR}")
endif()

file( GLOB_RECURSE ${PROJECT_NAME}_FILES
    README.md
    "${CMAKE_CURRENT_SOURCE_DIR}/*.py"
    "${CMAKE_CURRENT_SOURCE_DIR}/*.txt"
    "${CMAKE_CURRENT_SOURCE_DIR}/*.conf"
)

add_executable(example example.cpp
    ${${PROJECT_NAME}_FILES}
)
get_target_property(exe_location example LOCATION)
run_env_add_variable("exeloc" "${exe_location}")


add_test(generic_cpp_success example)
add_test(generic_cpp_failure example failure)

