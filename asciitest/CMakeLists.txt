# -*- coding: utf-8 -*-
#
# file: CMakeLists.txt (asciitest)
#
# Copyright 2011 - 2013 scitics GmbH
#

project( asciitest )

cmake_minimum_required(VERSION 2.8)

# [todo] - make configurable
file( GLOB_RECURSE ${PROJECT_NAME}_FILES  ${CMAKE_SOURCE_DIR}/DOC*.txt )

set(CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH} "${CMAKE_CURRENT_SOURCE_DIR}/CMakeModules/" )
find_package(Asciidoc)
find_package(PythonInterp)

if( PYTHONINTERP_FOUND )
    set(CONFIG_ASCIITEST_OUTDIR "${CMAKE_BINARY_DIR}/documentation")

    file(MAKE_DIRECTORY ${CONFIG_ASCIITEST_OUTDIR})

    # create a file containing all input files - we'll need it later to
    # get rid of tests which do not exist any more
    set(input_files_file "${CONFIG_ASCIITEST_OUTDIR}/asciitest-all_input_files.txt" )
    file( WRITE "${input_files_file}")
    foreach(filename ${${PROJECT_NAME}_FILES})
        file(APPEND "${input_files_file}" ${filename})
    endforeach()

    execute_process(COMMAND ${PYTHON_EXECUTABLE}
                    "${CMAKE_CURRENT_SOURCE_DIR}/asciitest-cmake_helpers.py"
                    "--generate-master" "-o" ${CONFIG_ASCIITEST_OUTDIR} )

    include("${CONFIG_ASCIITEST_OUTDIR}/asciitest-master.cmake")

    # [todo] - make configurable
    file( GLOB_RECURSE ${PROJECT_NAME}_FILTER_FILES plugins/* )

    function(install_asciidoc_filter filter_name filter_dir main_dependency)

        message("install_asciidoc_filter( filter='${filter_name}' main_dependency='${main_dependency}'")

        file( WRITE "${CMAKE_BINARY_DIR}/asciidoc-install-${filter_name}-plugin.cmake"
           "execute_process(COMMAND
                ${PYTHON_EXECUTABLE} ${ASCIIDOC_EXECUTABLE}
                        --filter build ${CMAKE_BINARY_DIR}/${filter_name}.zip ${filter_dir}
            )

            execute_process(COMMAND
                ${PYTHON_EXECUTABLE} ${ASCIIDOC_EXECUTABLE}
                        --filter remove ${filter_name}
            )

            execute_process(COMMAND
                ${PYTHON_EXECUTABLE} ${ASCIIDOC_EXECUTABLE}
                        --filter install ${CMAKE_BINARY_DIR}/${filter_name}.zip
            )
            "
        )
        add_custom_command(
            OUTPUT "${CMAKE_BINARY_DIR}/${filter_name}.zip"
            COMMAND ${CMAKE_COMMAND} -P "${CMAKE_BINARY_DIR}/asciidoc-install-${filter_name}-plugin.cmake"
            MAIN_DEPENDENCY
                    "${filter_dir}/${main_dependency}"
            COMMENT "create and install plugin for '${filter_name}'"
          )
        set( filter_dependencies ${filter_dependencies} "${CMAKE_BINARY_DIR}/${filter_name}.zip" PARENT_SCOPE )
    endfunction()

    option( CONFIG_INSTALL_EXTRA_ASCIIDOC_FILTERS "Create and install asciidoc filters" ON )
    if( CONFIG_INSTALL_EXTRA_ASCIIDOC_FILTERS )
        set( filter_dependencies ""  )
        # [todo] - make configurable
        install_asciidoc_filter( asciitest "${CMAKE_CURRENT_SOURCE_DIR}/asciitest_filter" asciitest_filter.py )
        #install_asciidoc_filter( plantuml acplantuml.py )
    endif()

    add_custom_target( ${PROJECT_NAME}
        SOURCES ${${PROJECT_NAME}_FILTER_FILES}
    )

    function( create_doc_html infile )

        get_filename_component( docname ${infile} NAME_WE )
        set( outvar_html "${CONFIG_ASCIITEST_OUTDIR}/${docname}.html" )

        add_custom_command(
            OUTPUT  ${outvar_html}
            COMMAND ${PYTHON_EXECUTABLE}
                    "${CMAKE_CURRENT_SOURCE_DIR}/asciitest-cmake_helpers.py"
                    "--cleanup" "-i" ${infile} "-o" ${CONFIG_ASCIITEST_OUTDIR}
            COMMAND ${PYTHON_EXECUTABLE}
                    ${ASCIIDOC_EXECUTABLE}
                    -a max-width=1024px
                    -a linkcss
                    -a stylesdir=style
                    -a stylesheet=Acme.css
                    -a disable-javascript
                    #-a badges
                    #-a icons
                    --out-file ${outvar_html}
                    ${infile}
            MAIN_DEPENDENCY
                    ${infile}
            WORKING_DIRECTORY
                    ${CMAKE_BINARY_DIR}
            COMMENT "Running asciidoc for html on \"${infile}\""
        )

        add_custom_target(doc-html-${docname}
            SOURCES  ${infile}
            DEPENDS  ${outvar_html} ${filter_dependencies}
        )

        add_dependencies( ${PROJECT_NAME}
            doc-html-${docname}
            #${filter_dependencies}
        )

    endfunction()

    foreach( var ${${PROJECT_NAME}_FILES} )
        create_doc_html( ${var} )
        message( "yyy ${var}" )
    endforeach()

else()

    message( WARNING "Python interpreter not found. Sexy HTML documentation won't be generated.." )
    
    # add documentation files to a dummy projet to have it easily accessible
    add_custom_target( ${PROJECT_NAME}_DEACTIVATED
        SOURCES ${${PROJECT_NAME}_FILES}
    )

endif()
