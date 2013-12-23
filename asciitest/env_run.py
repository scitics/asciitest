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
   be read from command line or from input file located at same place as
   executable
"""

from optparse import OptionParser
import subprocess
import os
import sys
import logging
import ast
import pprint


def add_path_to_env_variable(env, name, value):
    logging.debug("add to '%s': '%s'", name, value)
    if name in env and env[name].strip() != "":
        env[name] += os.pathsep + value
    else:
        env[name] = value


def read_config(directory, warn_if_file_not_existent=True):
    logging.error("using config dir: " + directory)
 
    try:
        _env_file_name = os.path.join(directory, "env_run_variables.txt")

        _values = {'PWD'        : os.getcwd(),
                   'ENVIRONMENT': ()}

        if not os.path.dirname(directory).startswith("/usr"):
            _values.update( ast.literal_eval(open(_env_file_name).read()) )
        else:
            _values = {}

        if not 'ENVIRONMENT' in _values:
            _values['ENVIRONMENT'] = ()
        if not 'PWD' in _values:
            # [todo] - test for existence
            _values['PWD'] = os.getcwd()

    except IOError, ex:
        if warn_if_file_not_existent:
            logging.warning("could not load environment variable file '%s'. "
                            "error was '%s'",
                            _env_file_name, ex)
    except SyntaxError, ex:
        logging.warning("syntax error in environment variable file. "
                        "error was '%s'", ex)
    except Exception, ex:
        logging.error("exception occured in read_config(): '%s'", ex)

    return _values


def write_config(directory, values):

    _env_file_name = os.path.join(directory, "env_run_variables.txt")

    try:
        _serialized_config = pprint.pformat(values) + '\n'
        values = open(_env_file_name, 'w').write(_serialized_config)

    except Exception, ex:
        logging.error("could not write environment variable file '%s'. "
                       "error was '%s'",
                       _env_file_name, ex)


def configure_variable(directory, key_value):
    try:

        if not '=' in key_value:
            logging.error("given variable definition '%s' is not valid", key_value)
            return

        pos = key_value.index('=')
        key, value = key_value[:pos], key_value[pos+1:]

        values = read_config(directory, warn_if_file_not_existent=False)

        logging.debug("configure new variable value '%s': '%s'", key, value)

        variable_definitions = set(values['ENVIRONMENT'])
        variable_definitions.add((key, value))
        values['ENVIRONMENT'] = list(variable_definitions)

        write_config(directory, values)

    except Exception, ex:
        logging.error("exception occured in configure_variable(): '%s'", ex)


def configure_pwd(directory, pwd):

    try:
        values = read_config(directory, warn_if_file_not_existent=False)

        _pwd = os.path.abspath(pwd)

        logging.debug("configure new pwd = '%s'", _pwd)

        values['PWD'] = _pwd

        write_config(directory, values)

    except Exception, ex:
        logging.error("exception occured in configure_pwd(): '%s'", ex)


def run(script_file, _config_output_dir, args, env):

    _python_exe = sys.executable

    _script_file = os.path.abspath(script_file)

    _env = os.environ.copy()

    _env.update(env)

    _env_file_dir = _config_output_dir
    
    _env_values = read_config(_env_file_dir)

    for key, value in _env_values['ENVIRONMENT']:
        add_path_to_env_variable(_env, key, value)

    # add this files directory, too
    add_path_to_env_variable( _env,
            'PYTHONPATH',
            os.path.dirname(os.path.abspath(__file__)))

    if _script_file.endswith('.py'):
        _args = [_python_exe, _script_file] + args
    else:
        _args = [_script_file] + args

    try:

        _process = subprocess.Popen(
            _args,
            # stdout=subprocess.PIPE,
            cwd     = _env_values['PWD'],
            env     = _env)

        _asciidoc_output = _process.communicate()[0]
        # print _asciidoc_output
        _return_value = _process.returncode
    except OSError, ex:
        logging.error("could not start process from args='%s', cwd='%s'",
                      _args, _env_values['PWD'])
        logging.error("error was '%s'", ex)
        _return_value = -1

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
        level=logging.WARNING)

    logging.addLevelName( logging.CRITICAL, '(CRITICAL)' )
    logging.addLevelName( logging.ERROR,    '(EE)' )
    logging.addLevelName( logging.WARNING,  '(WW)' )
    logging.addLevelName( logging.INFO,     '(II)' )
    logging.addLevelName( logging.DEBUG,    '(DD)' )
    logging.addLevelName( logging.NOTSET,   '(NA)' )

    _env = {}
    _config_output_dir = None

    logging.debug( "started with %s", str(sys.argv) )

    # we don't use OptionParser here because we want to pass all arguments
    # coming after the executable name
    _remaining_args = sys.argv[1:]

    while (len(_remaining_args) > 0
       and _remaining_args[0] in ('-p', '--python-executable',
                                  '-e', '--set-env',
                                  '--configure-variable',
                                  '--configure-pwd',
                                  '--config-output-dir')):

       if (len(_remaining_args) >= 2
           and _remaining_args[0] in ('--config-output-dir')):
           # in case a config output directory has been provided we save
           # it for later use
           _config_output_dir = _remaining_args[1]
           _remaining_args = _remaining_args[2:]

       if (len(_remaining_args) >= 2
           and _remaining_args[0] in ('--configure-variable')):
           if not _config_output_dir:
               logging.error("config output directory not set yet")
               sys.exit(-1)
           configure_variable(_config_output_dir, _remaining_args[1])
           _remaining_args = _remaining_args[2:]

       if (len(_remaining_args) >= 2
           and _remaining_args[0] in ('--configure-pwd')):
           if not _config_output_dir:
               logging.error("config output directory not set yet")
               sys.exit(-1)
           configure_pwd(_config_output_dir, _remaining_args[1])
           _remaining_args = _remaining_args[2:]

       if (len(_remaining_args) >= 2
          and _remaining_args[0] in ('-p', '--python-executable')):
           _python_executable = _remaining_args[1]
           _remaining_args = _remaining_args[2:]

       if (len(_remaining_args) >= 2
          and _remaining_args[0] in ('-e', '--set-env')):
           add_variable(_env,_remaining_args[1])
           _remaining_args = _remaining_args[2:]

    if len(_remaining_args) == 0:
        if _config_output_dir:
            # in case env_run was called in order to set values
            # everything is ok and we can quit
            sys.exit(0)
        else:
            # otherwise the user forgot something important
            logging.error("no script file given")
            sys.exit(-1)

    _script_file = _remaining_args[0]
    _remaining_args = _remaining_args[1:]

    sys.exit(run(_script_file, _config_output_dir, _remaining_args, _env))
