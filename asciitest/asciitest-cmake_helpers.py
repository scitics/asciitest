#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# file: asciitest-cmake_helpers.py
#
# Copyright 2011 - 2013 scitics GmbH
#
# Information  contained  herein  is  subject  to change  without  notice.
# scitics GmbH  retains ownership and  all other rights  in this software.
# Any reproduction of the software or components thereof without the prior
# written permission of scitics GmbH is prohibited.

from optparse import OptionParser
import os
import sys
import hashlib

def save_cmake_filename(filename):
    base_name = os.path.basename(os.path.abspath(filename.strip('\n ')))
    hash_name = "%s.cmake" % hashlib.sha1(base_name).hexdigest()[:20]
    #print("hash_name1: '%s' => '%s'" % (base_name, hash_name))
    return hash_name


def create_master(asciitest_out_dir):
    """ will create a .cmake include file containing an entry for all existing
        asciidoc files and makes these files exist
    """
    filename_out = os.path.join(asciitest_out_dir, "asciitest-master.cmake")
    filename_in = os.path.join(asciitest_out_dir, "asciitest-all_input_files.txt")
    with open(filename_out,'w') as f_out:
        for line in open(filename_in).readlines():
            f_out.write("# %s" % line)
            cmake_include_filename = os.path.join(
                asciitest_out_dir,
                save_cmake_filename(line))
            #print("create entry '%s'" %cmake_include_filename)
            f_out.write("include(%s)\n" % cmake_include_filename )
            open(cmake_include_filename, 'a').close()

def cleanup(asciitest_out_dir, doc_file):
    """remove all test files without corresponding doc files and remove 
       leftover test files which would not be created from their 
       corresponding doc files any more
    """
    filename = os.path.join(asciitest_out_dir, save_cmake_filename(doc_file))
    #print("cleanup %s %s" % (doc_file, filename))
    try:
        os.remove(filename)
    except:
        pass


if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("-i", "--input-file", dest="input_file",
                      help="file to clean up", metavar="FILE")
    parser.add_option("-o", "--out-dir", dest="out_dir",
                      help="asciitest directory to clean up", metavar="PATH")
    parser.add_option("--generate-master", dest="generate_master",
                      action="store_true", default = False,
                      help="asciitest directory to clean up")
    parser.add_option("--cleanup", dest="cleanup",
                      action="store_true", default = False,
                      help="trigger a clean up step")

    (options, args) = parser.parse_args()

    if options.generate_master:
        create_master(options.out_dir)

    if options.cleanup:
        cleanup(options.out_dir, options.input_file)

