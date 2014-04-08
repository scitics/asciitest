#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# file: env_run.py
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
import traceback

def add_path_to_env_variable(env, name, value):
    logging.debug("add to '%s': '%s'", name, value)
    if name in env and env[name].strip() != "":
        env[name] += os.pathsep + value
    else:
        env[name] = value


def read_config(directory, warn_if_file_not_existent=True):

    _values = {'PWD'        : os.getcwd(),
               'ENVIRONMENT': ()}

    try:
        _env_file_name = os.path.join(directory, "env_run_variables.txt")

        if not (os.path.dirname(directory).startswith("/usr")
            or directory.endswith("\\asciidoc")
            or directory.endswith("/asciidoc")):
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
        traceback.print_stack()
        logging.error("exception occured in read_config(): '%s'", ex)
        logging.error("args: %s", sys.argv)
    return _values


def write_config(directory, values):

    _env_file_name = os.path.join(directory, "env_run_variables.txt")

    try:
        _serialized_config = pprint.pformat(values) + '\n'
        values = open(_env_file_name, 'w').write(_serialized_config)

    except Exception, ex:
        traceback.print_stack()
        logging.error("could not write environment variable file '%s'. "
                       "error was '%s'",
                       _env_file_name, ex)
        logging.error("args: %s", sys.argv)


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
        traceback.print_stack()
        logging.error("exception occured in configure_variable(): '%s'", ex)
        logging.error("args: %s", sys.argv)


def configure_pwd(directory, pwd):

    try:
        values = read_config(directory, warn_if_file_not_existent=False)

        _pwd = os.path.abspath(pwd)

        logging.debug("configure new pwd = '%s'", _pwd)

        values['PWD'] = _pwd

        write_config(directory, values)

    except Exception, ex:
        traceback.print_stack()
        logging.error("exception occured in configure_pwd(): '%s'", ex)
        logging.error("args: %s", sys.argv)

def replace(variable_to_modify, content):
    for key, value in content.iteritems():
        #logging.warning("HHH %s %s", key, value)
        variable_to_modify = variable_to_modify.replace("$(%s)" % key, value)
    return variable_to_modify

def last_activity(path):
    mtime = 0
    for dirname, dirnames, filenames in os.walk(path):
        for filename in filenames:
            mtime = max(mtime, os.path.getmtime(os.path.join(dirname, filename)))
    return mtime

def guess_configuration_type(variables):
    for conf_variable in ("$(OutDir)", "$(Configuration)"):
        shortest_length = 1000
        base_path = None
        for key, value in variables:
            #logging.warning("aaaaa %s %s", conf_variable, value)
            if not conf_variable in value: continue
            #logging.warning("bbbbb")
            pathname = os.path.abspath(value)
            effective_length = pathname.find(conf_variable)
            if effective_length < shortest_length:
                shortest_length = effective_length
                base_path = pathname[:effective_length]
                
        if base_path == None: continue
            
        debug_path = os.path.join(base_path, 'Debug')
        release_path = os.path.join(base_path, 'Release')
        debug_exists = os.path.exists(debug_path)
        release_exists = os.path.exists(release_path)
        
        if not (debug_exists or release_exists): continue
        
        if debug_exists and not release_exists:
            return 'Debug'
            
        if release_exists and not debug_exists:
            return 'Release'

        #logging.warning("cccccc %f %f", last_activity(debug_path), last_activity(release_path))
            
        if last_activity(debug_path) > last_activity(release_path):
            return 'Debug'
        else:
            return 'Release'
            
    return None
    
def run(script_file, args, env):

    _python_exe = sys.executable

    _script_file = os.path.abspath(script_file)

    _env_file_dir = os.path.dirname(_script_file)

    _env_values = read_config(_env_file_dir)

    # for visual studio we guess the last built configuration type
    conf_type = guess_configuration_type(_env_values['ENVIRONMENT'])
    
    if conf_type:
        env['OutDir'] = conf_type
        env['Configuration'] = conf_type
    
    #logging.warning("guessed %s", conf_type)
    _env = os.environ.copy()

    _env.update(env)

    for key, value in _env_values['ENVIRONMENT']:
        new_value = replace(value, env)
        #logging.warning("YYY %s %s", value, new_value)
        add_path_to_env_variable(_env, key, new_value)

    # add this files directory, too
    add_path_to_env_variable( _env,
            'PYTHONPATH',
            os.path.dirname(os.path.abspath(__file__)))

    if _script_file.endswith('.py'):
        _args = [_python_exe, _script_file] + args
    else:
        _args = [_script_file] + args

    try:
        #logging.warning("XXX %s", _env['YSBOX_IMPORTER'] if 'YSBOX_IMPORTER' in _env else "---")
        _process = subprocess.Popen(
            _args,
            # stdout=subprocess.PIPE,
            cwd     = _env_values['PWD'],
            env     = _env)

        _process_output = _process.communicate()
        _return_value = _process.returncode
        #print _process_output, _return_value
        
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
    #logging.warning("VVV '%s'='%s'", variable[:pos],variable[pos+1:])
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

    # we don't use OptionParser here because we want to pass all arguments
    # coming after the executable name
    _remaining_args = sys.argv[1:]

    while (len(_remaining_args) > 0
       and _remaining_args[0] in ('-v', '--verbose',
                                  '-p', '--python-executable',
                                  '-e', '--set-env',
                                  '-g', '--get-env',
                                  '--configure-variable',
                                  '--configure-pwd',
                                  '--config-output-dir')):

        if (len(_remaining_args) >= 1
           and _remaining_args[0] in ('-v', '--verbose')):
            # in case a config output directory has been provided we save
            # it for later use
            logging.getLogger().setLevel(logging.DEBUG)
            _remaining_args = _remaining_args[1:]

        if (len(_remaining_args) >= 2
           and _remaining_args[0] in ('--config-output-dir')):
            # in case a config output directory has been provided we save
            # it for later use
            _config_output_dir = _remaining_args[1]
            _remaining_args = _remaining_args[2:]

        if (len(_remaining_args) >= 2
           and _remaining_args[0] in ('-g', '--get-env')):
            if _remaining_args[1] in os.environ:
                print(os.environ[_remaining_args[1]])
            else:
                print("")
            sys.exit(0)

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

    logging.info( "started with %s", str(sys.argv) )

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

    logging.debug("script file:       '%s'", _script_file)
    logging.debug("config_output_dir: '%s'", _config_output_dir)
    logging.debug("args:              '%s'", _remaining_args)
    logging.debug("env:               '%s'", _env)

    sys.exit(run(_script_file, _remaining_args, _env))


