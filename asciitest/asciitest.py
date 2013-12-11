#!/usr/bin/python
# -*- coding: utf-8 -*-
# file: test/test-server-wiki_import.py

import sys
import time

last_counter = -1
result_file = None
log_file = None
test_doc_file = "MISSING-test_doc_file"
test_name = "MISSING-test_name"
base_time = time.time()

class subtest:
    def __init__(self, condition, description):
        self.result = None
        self.condition = condition
        self.description = description

subtests = {}

def write_result_line( message ):
    global result_file
    if len(message) == 0:
        return
    sys.stdout.write("RESULT: %s" % str( message ) )
    if result_file: result_file.write( str( message ) )
    if not (type(message) is str and len(message)>0 and message[-1] == '\n'):
        sys.stdout.write("\n")
        if result_file: result_file.write("\n")

def write_log( message ):
    global log_file
    if len(message) == 0:
        return
    sys.stdout.write("DEBUG: %s" % str( message ) )
    if log_file: log_file.write( str( message ) )
    if not (type(message) is str and len(message)>0 and message[-1] == '\n'):
        sys.stdout.write("\n")
        if log_file: log_file.write("\n")

def set_result_file( file_name ):
    global result_file
    if file_name:
        result_file = open( file_name,'w' )
    else:
        result_file = None

def set_log_file( file_name ):
    global log_file
    if file_name:
        log_file = open( file_name,'w' )
    else:
        log_file = None

def register_subtest(count, condition, description):
    global subtests
    subtests[count] = subtest(condition, description)
    write_result_line( 'self.subtests[%d] = subtest( "%s", "%s" )' % (
        count,
        condition.replace("\"","\\\"").replace("\'","\\\'"),
        description ) )

def start_tests( testDocFile, testName, filename="deprecated" ):
    global last_counter, test_doc_file, test_name, base_time
    last_counter = -1
    test_doc_file = testDocFile
    test_name = testName
    base_time = time.time() * 1000.0
    write_result_line( 'self.source_name="%s"'%testDocFile )
    write_result_line( 'self.test_name="%s"'%testName )
    write_result_line( 'self.test_language="python"' )
    

def finalize_tests():
    pass

def notify_result( counter, result ):
    global last_counter, subtests, base_time

    if counter != last_counter + 1:
        write_log( "ERROR: a sub test has been skipped!\n" )
    try:
        new_time = time.time() * 1000.0
        last_counter = counter

        write_result_line( "self.subtests[%d].executed = %s" % (
            counter, "True" ) )
        write_result_line( "self.subtests[%d].time = %f" % (
            counter, time.time() ) )
        write_result_line( "self.subtests[%d].execution_time = %f" % (
            counter, new_time - base_time ) )
        write_result_line( "self.subtests[%d].test_ok = %s" % (
            counter, "True" if result else "False" ) )

        base_time = time.time() * 1000.0
    except Exception, ex:
        write_log("ERROR:" + str(ex))
