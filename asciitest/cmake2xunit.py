#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# file: cmake2xunit.py
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

from lxml import etree
import StringIO
import sys
import os
import optparse
import logging

def convert(directory, xsl_filename, out_filename):

    tag_filename = os.path.join(os.path.abspath(directory), "Testing/TAG")

    try:
        dirname = open(tag_filename , 'r').readline().strip()
    except:
        logging.error("could not open tag file '%s'", tag_filename)
        sys.exit(-1)

    xml_filename = os.path.join(directory, "Testing/", dirname, "Test.xml")

    try:
        xmlcontent = open(xml_filename, 'r').read()
    except:
        logging.error("could not open xml file '%s'", xml_filename)
        sys.exit(-1)

    try:
        xslcontent = open(xsl_filename, 'r').read()
    except:
        logging.error("could not open xsl file '%s'", xsl_filename)
        sys.exit(-1)

    xmldoc = etree.parse(StringIO.StringIO(xmlcontent))
    xslt_root = etree.XML(xslcontent)
    transform = etree.XSLT(xslt_root)

    result_tree = transform(xmldoc)

    #print dir(result_tree)

    if out_filename:
        open(out_filename, 'w').write(str(result_tree))
    else:
        print(result_tree)

if __name__ == "__main__":
    parser = optparse.OptionParser()
    parser.add_option("-d", "--input-directory", dest="input_directory",
                      default = ".",
                      help="file to clean up", metavar="FILE")

    parser.add_option("-x", "--xsl-file", dest="xsl_file",
                      help="file to clean up", metavar="FILE")

    parser.add_option("-o", "--output-file", dest="out_file",
                      help="file to clean up", metavar="FILE")

    (options, args) = parser.parse_args()

    if options.xsl_file:
        _xslfile = options.xsl_file
        if not os.path.exists(_xslfile):
            print("provided xsl file '%s' does not exist" % _xslfile)
            sys.exit(-1)
    else:
        _xslfile = os.path.join(os.path.dirname(__file__), "cmake2xunit.xsl")
        if not os.path.exists(_xslfile):
            print("no xsl file provided and '%s' does not exist" % _xslfile)
            sys.exit(-1)

    _input_dir = options.input_directory

    convert(_input_dir, _xslfile, options.out_file)

