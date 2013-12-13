#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# file: env_run.py
#
# Copyright 2011 - 2013 scitics GmbH
#
# Information  contained  herein  is  subject  to change  without  notice.
# scitics GmbH  retains ownership and  all other rights  in this software.
# Any reproduction of the software or components thereof without the prior
# written permission of scitics GmbH is prohibited.

""" runs a python script with additional enviroment variables"""

from optparse import OptionParser
import subprocess
import os
import sys

def run(script_file):

    _python_exe = sys.executable

    _env = os.environ.copy()

    _env[ 'PYTHONPATH'     ] = os.path.dirname(os.path.abspath(__file__))

    _process = subprocess.Popen(
        [sys.executable, script_file],
        # stdout=subprocess.PIPE,
        env = _env)

    _asciidoc_output = _process.communicate()[0]

    # print _asciidoc_output

    _return_value = _process.returncode

    return _return_value



if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("-p", "--python-executable", dest="python_executable",
                      help="file to clean up", metavar="FILE")
    parser.add_option("-e", "--executable_file", dest="executable_file",
                      help="file to clean up", metavar="FILE")

    (options, args) = parser.parse_args()

    if not options.executable_file and len(args) == 0:
        print("no script file given")
        sys.exit(-1)

    if options.executable_file:
        _script_file = options.executable_file
    else:
        _script_file = args[0]

    sys.exit(run(_script_file))
