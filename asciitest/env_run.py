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
import logging
import ast

def add_path_to_env_variable(env, name, value):
    logging.debug("add to '%s': '%s'", name, value)
    if name in env and env[name].strip() != "":
        env[name] += os.pathsep + value
    else:
        env[name] = value


def run(script_file):

    _python_exe = sys.executable

    _script_file = os.path.abspath(script_file)

    _env = os.environ.copy()

    env_file_name = os.path.join(
            os.path.dirname(_script_file),
            "env_run_variables.txt")

    _cwd = os.getcwd()

    try:
        values = ast.literal_eval(open(env_file_name).read())
        if 'ENVIRONMENT' in values:
            for key, value in values['ENVIRONMENT']:
                add_path_to_env_variable(_env, key, value)
        if 'PWD' in values:
            _cwd = values['PWD']
    except IOError, ex:
        logging.warning("could not load environment variable file '%s'. "
                        "error was '%s'",
                        env_file_name, ex)
    except SyntaxError, ex:
        logging.warning("syntax error in environment variable file. "
                        "error was '%s'", ex)

    add_path_to_env_variable( _env,
            'PYTHONPATH',
            os.path.dirname(os.path.abspath(__file__)))

    _process = subprocess.Popen(
        [sys.executable, _script_file],
        # stdout=subprocess.PIPE,
        cwd     = _cwd,
        env     = _env)

    _asciidoc_output = _process.communicate()[0]

    # print _asciidoc_output

    _return_value = _process.returncode

    return _return_value



if __name__ == "__main__":
    logging.basicConfig(
        format='%(asctime)s [env_run] %(levelname)s %(message)s',
        datefmt="%y%m%d-%H%M%S",
        level=logging.DEBUG)

    logging.addLevelName( logging.CRITICAL, '(CRITICAL)' )
    logging.addLevelName( logging.ERROR,    '(EE)' )
    logging.addLevelName( logging.WARNING,  '(WW)' )
    logging.addLevelName( logging.INFO,     '(II)' )
    logging.addLevelName( logging.DEBUG,    '(DD)' )
    logging.addLevelName( logging.NOTSET,   '(NA)' )

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
