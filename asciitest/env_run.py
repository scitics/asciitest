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

"""runs an executable file with additional enviroment variables which can
   be red from command line or from input file located at same place as
   executable
"""

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

def run(script_file, args, env):

    _python_exe = sys.executable

    _script_file = os.path.abspath(script_file)

    _env = os.environ.copy()

    _env.update(env)

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

    if _script_file.endswith('.py'):
        _args = [_python_exe, _script_file] + args
    else:
        _args = [_script_file] + args

    _process = subprocess.Popen(
        _args,
        # stdout=subprocess.PIPE,
        cwd     = _cwd,
        env     = _env)

    _asciidoc_output = _process.communicate()[0]

    # print _asciidoc_output

    _return_value = _process.returncode

    return _return_value

def add_variable(env, variable):
    if not '=' in variable:
        logging.error("given variable definition '%s' is not valid", variable)
        return
    pos = variable.index('=')
    env[variable[:pos]] = variable[pos+1:]

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

    _env = {}

    # we don't use OptionParser here because we want to pass all arguments
    # coming after the executable name
    _remaining_args = sys.argv[1:]
    while (len(_remaining_args) > 0
       and _remaining_args[0] in ('-p', '--python-executable', '-e', '--set-env')):

       if (len(_remaining_args) >= 2
          and _remaining_args[0] in ('-p', '--python-executable')):
           _python_executable = _remaining_args[1]
           _remaining_args = _remaining_args[2:]

       if (len(_remaining_args) >= 2
          and _remaining_args[0] in ('-e', '--set-env')):
           add_variable(_env,_remaining_args[1])
           _remaining_args = _remaining_args[2:]

    if len(_remaining_args) == 0:
        logging.error("no script file given")
        sys.exit(-1)

    _script_file = _remaining_args[0]
    _remaining_args = _remaining_args[1:]

    sys.exit(run(_script_file, _remaining_args, _env))
