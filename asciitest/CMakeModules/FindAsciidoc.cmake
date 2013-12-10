# -*- coding: utf-8 -*-
#
# file: FindAsciidoc.cmake
#
# Copyright 2011 - 2013 scitics GmbH
#
# This module locates the asciidoc executable which converts ASCII files written
# in a simple text markup into various output formats.
#
# The module sets the following cache variables
# - ASCIIDOC_EXECUTABLE the asciidoc executable
# - A2X_EXECUTABLE the a2x executable (only on UNIX systems)
#

# search the asciidoc executable

find_program( ASCIIDOC_EXECUTABLE NAMES asciidoc asciidoc.py )
set( __AsciiDoc_VARS ASCIIDOC_EXECUTABLE )

if( UNIX )
  find_program( A2X_EXECUTABLE NAMES a2x a2x.sh )
  list( APPEND __AsciiDoc_VARS A2X_EXECUTABLE )
endif( UNIX )

mark_as_advanced( ${__AsciiDoc_VARS} )

include( FindPackageHandleStandardArgs )
find_package_handle_standard_args( AsciiDoc DEFAULT_MSG ${__AsciiDoc_VARS} )
