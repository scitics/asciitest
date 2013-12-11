#!/usr/bin/python
# -*- coding: utf-8 -*-

from optparse import OptionParser
import os
import sys
import hashlib

def save_cmake_filename(filename):
    return "%s.cmake" % hashlib.sha1(os.path.basename(filename)).hexdigest()[:20]

def create_master(asciitest_out_dir):
    filename_out = os.path.join(asciitest_out_dir, "asciitest-master.cmake")
    filename_in = os.path.join(asciitest_out_dir, "asciitest-all_input_files.txt")
    with open(filename_out,'w') as f_out:
        for line in open(filename_in).readlines():
            f_out.write("# %s\n" % line)
            f_out.write("# include %s\n" % save_cmake_filename(line))

def cleanup(asciitest_out_dir, doc_file):
    """remove all test files without corresponding doc files and remove 
       leftover test files which would not be created from their 
       corresponding doc files any more
    """
    filename = os.path.join(asciitest_out_dir, save_cmake_filename(doc_file))
    print("cleanup %s %s" % (doc_file, filename))


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
                      help="asciitest directory to clean up")

    (options, args) = parser.parse_args()

    if options.generate_master:
        create_master(options.out_dir)

    if options.cleanup:
        cleanup(options.out_dir, options.input_file)

