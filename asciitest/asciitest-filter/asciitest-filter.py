#!/usr/bin/env python
'''
NAME
    asciitest-filter - AsciiDoc filter for generating test code from asciidoc files

SYNOPSIS
    asciitest-filter -b backend -l language [ -t tabsize ]
                [ --help | -h ] [ --version | -v ]

DESCRIPTION
    please describe me!

OPTIONS
    --help, -h
        Print this documentation.

    -b
        Backend output file format: 'docbook', 'linuxdoc', 'html', 'css'.

    -l
        The name of the source code language: 'python', 'ruby', 'c++', 'c'.

    -t tabsize
        Expand source tabs to tabsize spaces.

    --version, -v
        Print program version number.

BUGS
    - no bugs
    
AUTHOR
    Written by Frans Fuerst, <frans.fuerst@scitics.de>

URLS
    http://sourceforge.net/projects/asciidoc/
    http://www.methods.co.nz/asciidoc/

COPYING
    Copyright (C) 2012-2013 scitics GmbH. Free use of this software is
    granted under the terms of the GNU General Public License (GPL).
'''

import os
import sys
import re
import string
import logging
from optparse import OptionParser

VERSION = '1.0'

language = None
backend = None
document_name = None
tabsize = 4
test_type = None

keywordtags = {
    'html':
        ('<strong>','</strong>'),
    'css':
        ('<strong>','</strong>'),
    'docbook':
        ('<emphasis role="strong">','</emphasis>'),
    'linuxdoc':
        ('','')
}

languages = ['text', 'python', 'c++']

def code_filter():

    '''This function does all the work.'''
    global language, backend, document_name, test_type, test_name

    line_sep = os.linesep

    if language == "text":
        filename = test_name
        logging.info( "create a text file called '%s'", filename )
        f = open( filename, 'w' )
        #TODO: create files called INPUT-<test-file-name>-<test-file>
        content = sys.stdin.read()
        sys.stdout.write( content + line_sep )
        f.write         ( content + line_sep )
        f.close()

    elif language == "c++":
        subtest_counter = 0

        test_filename   = "../test/include/TEST-%s-%s.cpp"%(document_name, test_name)
        result_filename = "RESULT-%s-%s.csv"%(document_name, test_name)
        logging.info( "create a python script called '%s'" % test_filename )
        f = open( test_filename, 'w' )
        f.write( '/** automatically generated test file */ ' + line_sep )
        f.write( '#include <tests/TestEnvironment.h>'          + line_sep )
        f.write( ''                            + line_sep )
        f.write( 'TestEnvironment AcmeTest;'  + line_sep )
        f.write( ''                            + line_sep )
        f.write( 'void test()'                 + line_sep )
        f.write( '{'                           + line_sep )
        f.write( '    AcmeTest.start_tests("%s","%s","%s");'
                           % (document_name, test_name, result_filename) + line_sep )

        #TODO: write something like
        #for f in (INPUT-client_lib-*):
        #    cp( f strip(f, "INPUT-client_lib-" )


        line = sys.stdin.readline()
        while line:
            # format the line
            line = string.rstrip(line)
            # expand tabs
            line = string.expandtabs(line,tabsize)
            # do some preprocessing
            #line = string.replace(line,'&','&amp;')
            #line = string.replace(line,'<','&lt;')
            #line = string.replace(line,'>','&gt;')

            sys.stdout.write( line + line_sep )

            if "TEST(" in line:
                line = line.replace( "TEST(", "AcmeTest.notify_result( %d, "
                        %  (subtest_counter ) )
                subtest_counter += 1

            f.write("    "  + line + line_sep )

            line = sys.stdin.readline()

        f.write( '    AcmeTest.finalize_tests();'   + line_sep )
        f.write( '}'                                 + line_sep )
        f.write( 'int main(int argc, char *argv[])'  + line_sep )
        f.write( '{'                                 + line_sep )
        f.write( '    AcmeTest.init(argc, argv);'   + line_sep )
        f.write( '    test();'                       + line_sep )
        f.write( '}'                                 + line_sep )
        f.close()

    elif language == "python":
        subtest_counter = 0

        test_filename = "TEST-%s-%s.py"%(document_name, test_name)

        logging.info( "create a python script called '%s'", test_filename )

        test_defs = []
        dynamic_code = []

        while True:
            line = sys.stdin.readline()
            if not line: break

            # format the line
            line = string.expandtabs( string.rstrip( line ), tabsize )

            # output the line to make the test visible in the resulting
            # file
            print ":%s" % line

            if "TEST(" in line:
                # from "TEST(<condition>, <description>)"
                # create a line
                # "AcmeTest.register_subtest(<counter>,'<condition>', <description>)"
                # and replace the original by
                # "AcmeTest.notify_result(<counter>, <condition>)"
                #logging.info("found a test line '%s'"%line)


                guts = line.strip()
                guts = guts[guts.find('TEST(') + 5 :-1].strip()
                #logging.info( "guts: '%s'"%guts)

                PATTERN = re.compile(r'''((?:[^,"']|"[^"]*"|'[^']*')+)''')
                guts = PATTERN.split(guts)
                #logging.info( guts )
                #logging.info( len(guts) )
                #logging.info( guts[1::2] )

                # extract and escape the condition component
                #test_condition = line[line.find('(') + 1 :line.find(',')].strip()
                test_condition = guts[1]
                #logging.info("condition is '%s'"%test_condition)

                test_description = guts[3]
                #test_description = line[line.find(',') + 1 :line.find(')')].strip(' \'\"')
                logging.info("added a test for %s" % test_description)

                test_defs.append( 'asciitest.register_subtest( %d, "%s",'
                    %  (subtest_counter,
                        test_condition.replace("\"","\\\"").replace("\'","\\\'") )
                    + line[line.find(',') + 1 :])

                dynamic_code.append( "    " +  line_sep )
                dynamic_code.append( "    " + "# TEST: %s"%
                    test_description   + line_sep )
                line = line.replace('TEST', 'asciitest.notify_result')
                line = "%s( %d, %s )" % (
                        line[:line.find('(')],
                        subtest_counter, test_condition )
                dynamic_code.append( "    "  + line + line_sep )
                subtest_counter += 1
            else:
                dynamic_code.append( "    "  + line + line_sep )

        with open( test_filename, 'w' ) as f:

            f.write( '#!/usr/bin/python'                     + line_sep )
            f.write( '# -*- coding: utf-8 -*-'               + line_sep )
            f.write( ''                                      + line_sep )
            f.write( 'import asciitest'                      + line_sep )
            f.write( 'from optparse import OptionParser'     + line_sep )
            f.write( 'import sys'                            + line_sep )
            f.write( ''                                      + line_sep )

            #f.write( 'import AcmeClientPython'               + line_sep )
            #f.write( 'import sys'                            + line_sep )
            #f.write( 'import os'                             + line_sep )

            f.write( ''                                      + line_sep )
            f.write( 'def register_tests():'                 + line_sep )
            f.write( ''                                      + line_sep )

            for t in test_defs:
                f.write( '    ' + t                          + line_sep )
            f.write( '    pass'                              + line_sep )
            f.write( ''                                      + line_sep )

            f.write( 'def run_subtests():'                   + line_sep )

            #if test_type and test_type == "acme_integration_test":
            #    f.write( '    server, server_id, connection_state = AcmeTest.begin_acme_integration_test()' + line_sep )

            #TODO: write something like
            #for f in (INPUT-client_lib-*):
            #    cp( f strip(f, "INPUT-client_lib-" )

            for l in dynamic_code:
                f.write( l )

            #if test_type and test_type == "acme_integration_test":
            #    f.write( '    AcmeTest.end_acme_integration_test(server, server_id, connection_state)' + line_sep )

            f.write( '    pass'                              + line_sep )
            f.write( ''                                      + line_sep )
            f.write( 'def run_tests():'                      + line_sep )
            f.write( '    parser = OptionParser()'           + line_sep )
            f.write( '    parser.add_option("-r", "--result-file", dest="result_file",'        + line_sep )
            f.write( '                      help="write result file", metavar="result-file")'  + line_sep )
            f.write( '    parser.add_option("-l", "--log-file", dest="log_file",'              + line_sep )
            f.write( '                     help="write log to file", metavar="log_file")'      + line_sep )
            f.write( '    parser.add_option("-b", "--acme_binary", dest="acme_binary",'           + line_sep )
            f.write( '                     help="path to the acme binary to be used", metavar="FILE")'   + line_sep )
            f.write( '    parser.add_option("-v", "--verbose", dest="verbose", default=False,'                  + line_sep )
            f.write( '                      action="store_true", help="set verbosity on", metavar="verbosity")' + line_sep )
            f.write( '    (options, args) = parser.parse_args()'                                                + line_sep )
            f.write( '    if options.result_file: asciitest.set_result_file( options.result_file )'             + line_sep )
            f.write( '    if options.log_file:    asciitest.set_log_file( options.log_file )'                   + line_sep )
            f.write( '    if options.acme_binary: asciitest.set_acme_binary( options.acme_binary )'             + line_sep )
            f.write( '    asciitest.start_tests("%s","%s")'
                               % (document_name, test_name)  + line_sep )
            f.write( '    register_tests()'                                  + line_sep )
            f.write( '    ret_val = 0'                                       + line_sep )
            f.write( '    try:'                                              + line_sep )
            f.write( '        run_subtests()'                                + line_sep )
            f.write( '    except Exception, ex:'                             + line_sep )
            f.write( '        print "Error executing test"'                  + line_sep )
            f.write( '        print ex'                                      + line_sep )
            f.write( '        ret_val = -1'                                  + line_sep )
            f.write( '    asciitest.finalize_tests()'                        + line_sep )
            f.write( '    sys.exit(ret_val)'                                 + line_sep )
            f.write( ''                                                      + line_sep )
            f.write( 'if __name__ == "__main__":'                            + line_sep )
            f.write( '    run_tests()'                                       + line_sep )

    elif language == "python_acme_":
        pass

def main():
    global language, backend, tabsize, test_name, document_name, test_type

    parser = OptionParser(usage="usage: %prog [options]")


    parser.add_option("-b", "--backend", dest="backend",
                      default="html",
                      metavar="NAME",
                      help="name of the asciidoc backend to be used")

    parser.add_option("-d", "--document", dest="document",
                      metavar="FILENAME",
                      help="name of the input document")

    parser.add_option("-V", "--version", dest="version",
                      action="store_true", default = False,
                      help = "be more verbose")

    parser.add_option("-v", "--verbose", dest="verbose",
                      action="store_true", default = False,
                      help = "be more verbose")

    parser.add_option("-u", "--unit-name", dest="test_name",
                      metavar="NAME",
                      help="name of the given test unit")

    parser.add_option("-l", "--language", dest="language",
                      metavar="LANGUAGE",
                      help="python|c++|text")

    parser.add_option("-y", "--test-type", dest="type",
                      metavar="TYPE",
                      help="test specialization")

    parser.add_option("-t", "--tabsize", dest="tabsize",
                      metavar="SIZE",
                      help="indentation size")


    (options, args) = parser.parse_args()

    if len(args) > 0:
        parser.print_help()
        logging.error( "unrecognized parameter '%s'" % args )
        sys.exit(-1)

    if options.version:
        logging.error('asciitest-filter version %s' % (VERSION,))
        sys.exit(0)

    if options.backend and options.backend in keywordtags:
        backend = options.backend
    else:
        logging.error('backend must be set and must be one of %s' % str(keywordtags.keys()))
        parser.print_help()
        sys.exit(-1)

    if options.document:
        document_name = options.document
        if(document_name.startswith("DOC")):
            document_name = document_name[4:]
    else:
        logging.error('document name must be set')
        parser.print_help()
        sys.exit(-1)

    if options.test_name:
        test_name = options.test_name
    else:
        logging.error('test name must be set')
        parser.print_help()
        sys.exit(-1)

    if options.language and options.language in languages:
        language = options.language
    else:
        logging.error('language must be set and must be one of %s' % str(languages))
        parser.print_help()
        sys.exit(-1)

    if options.type:
        test_type = options.type

    if options.tabsize:
        try:
            tabsize = int(options.tabsize)
        except:
            print('tab size invalid')
            parser.print_help()
            sys.exit(-1)

    code_filter()


if __name__ == "__main__":
    logging.basicConfig(
        format='%(asctime)s %(levelname)s %(message)s',
        datefmt="%y%m%d-%H%M%S")
    logging.getLogger().setLevel(logging.DEBUG)
    
    logging.addLevelName( logging.CRITICAL, '(CRITICAL)' )
    logging.addLevelName( logging.ERROR,    '(EE)' )
    logging.addLevelName( logging.WARNING,  '(WW)' )
    logging.addLevelName( logging.INFO,     '(II)' )
    logging.addLevelName( logging.DEBUG,    '(DD)' )
    logging.addLevelName( logging.NOTSET,   '(NA)' )
    
    logging.info( "'%s'"% sys.argv )
    try:
        main()

    except (KeyboardInterrupt, SystemExit):
        pass
    except:
        logging.info("%s: unexpected exit status: %s" %
            (os.path.basename(sys.argv[0]), sys.exc_info()[1]))
    # exit with previous sys.exit() status or zero if no sys.exit().
    sys.exit(sys.exc_info()[1])

