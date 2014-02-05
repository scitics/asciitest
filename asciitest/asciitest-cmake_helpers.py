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
import errno
import sys
import hashlib

def silentremove(filename):
    try:
        os.remove(filename)
    except OSError as e:
        if e.errno != errno.ENOENT:
            raise

def save_cmake_filename(filename):
    base_name = os.path.basename(os.path.abspath(filename.strip('\n ')))
    hash_name = "%s.cmake" % hashlib.sha1(base_name).hexdigest()[:20]
    #print("hash_name1: '%s' => '%s'" % (base_name, hash_name))
    return hash_name

def update_if_different(filename1, filename2):

    hash1 = hashlib.sha256()
    hash2 = hashlib.sha256()

    try:
        hash1 = hashlib.sha256(open(filename1, 'rb').read())
        hash2 = hashlib.sha256(open(filename2, 'rb').read())
    except:
        #print "failed to create a hash"
        pass

    if hash1.digest() == hash2.digest():
        #print "hashes are equal - remove temp file '%s'" % filename1

        try:
            silentremove(filename1)
        except:
            print "could not remove file '%s'" % filename1
    else:
        print "hashes differ (%s:%s) rename '%s'"% (hash1.hexdigest(), hash2.hexdigest(), filename1)
        try:
            silentremove(filename2)
            os.rename(filename1, filename2)
        except Exception, ex:
            print "could not rename file '%s' to '%s'" % (filename1, filename2)
            print "error was '%s'" % ex


def create_master(asciitest_out_dir):
    """ will create a .cmake include file containing an entry for all existing
        asciidoc files and makes these files exist
    """
    # path join uses backslash under windows which is not cmake compatible
    filename_out = os.path.join(asciitest_out_dir, "asciitest-master.cmake").replace("\\","/")
    # path join uses backslash under windows which is not cmake compatible
    filename_in = os.path.join(asciitest_out_dir, "asciitest-all_input_files.txt").replace("\\","/")

    with open(filename_out + ".temp", 'w') as f_out:
        for line in open(filename_in).readlines():
            f_out.write("# %s" % line)
            # path join uses backslash win32 which is not cmake compatible
            cmake_include_filename = os.path.join(
                asciitest_out_dir,
                save_cmake_filename(line)).replace("\\", "/")
            #print("create entry '%s'" %cmake_include_filename)
            f_out.write("include(%s)\n" % cmake_include_filename )
            open(cmake_include_filename, 'a').close()

    update_if_different(filename_out + ".temp", filename_out)

def cleanup(asciitest_out_dir, doc_file):
    """remove all test files without corresponding doc files and remove 
       leftover test files which would not be created from their 
       corresponding doc files any more
    """
    # path join uses backslash win32 which is not cmake compatible
    filename = os.path.join(asciitest_out_dir, save_cmake_filename(doc_file)).replace("\\","/")
    
    #print("cleanup %s %s" % (doc_file, filename))
    try:
        os.remove(filename)
    except:
        pass

def conditional_copy(asciitest_out_dir, doc_file):
    """remove all test files without corresponding doc files and remove
       leftover test files which would not be created from their
       corresponding doc files any more
    """
    # path join uses backslash win32 which is not cmake compatible

    filename = save_cmake_filename(doc_file)

    filename1 = os.path.join(asciitest_out_dir, filename + ".temp").replace("\\","/")
    filename2 = os.path.join(asciitest_out_dir, filename).replace("\\","/")

    update_if_different(filename1, filename2)


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
    parser.add_option("--conditional-copy", dest="conditional_copy",
                      action="store_true", default = False,
                      help="applies a given temporary input file if different")

    (options, args) = parser.parse_args()

    if options.generate_master:
        create_master(options.out_dir)

    if options.cleanup:
        cleanup(options.out_dir, options.input_file)

    if options.conditional_copy:
        conditional_copy(options.out_dir, options.input_file)
