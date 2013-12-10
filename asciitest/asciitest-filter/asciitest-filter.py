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

VERSION = '1.0'

# Globals.
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


def code_filter():

    '''This function does all the work.'''
    global language, backend, document_name, test_type, test_name

    if language == "text":
        filename = test_name
        logging.info( "create a text file called '%s'", filename )
        f = open( filename, 'w' )
        #TODO: create files called INPUT-<test-file-name>-<test-file>
        content = sys.stdin.read()
        sys.stdout.write( content + os.linesep )
        f.write         ( content + os.linesep )
        f.close()
    elif language == "c++":
        subtest_counter = 0

        test_filename   = "../test/include/TEST-%s-%s.cpp"%(document_name, test_name)
        result_filename = "RESULT-%s-%s.csv"%(document_name, test_name)
        logging.info( "create a python script called '%s'" % test_filename )
        f = open( test_filename, 'w' )
        f.write( '/** automatically generated test file */ ' + os.linesep )
        f.write( '#include <tests/TestEnvironment.h>'          + os.linesep )
        f.write( ''                            + os.linesep )
        f.write( 'TestEnvironment AcmeTest;'  + os.linesep )
        f.write( ''                            + os.linesep )
        f.write( 'void test()'                 + os.linesep )
        f.write( '{'                           + os.linesep )
        f.write( '    AcmeTest.start_tests("%s","%s","%s");'
                           % (document_name, test_name, result_filename) + os.linesep )

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

            sys.stdout.write( line + os.linesep )

            if "TEST(" in line:
                line = line.replace( "TEST(", "AcmeTest.notify_result( %d, "
                        %  (subtest_counter ) )
                subtest_counter += 1

            f.write("    "  + line + os.linesep )

            line = sys.stdin.readline()

        f.write( '    AcmeTest.finalize_tests();'   + os.linesep )
        f.write( '}'                                 + os.linesep )
        f.write( 'int main(int argc, char *argv[])'  + os.linesep )
        f.write( '{'                                 + os.linesep )
        f.write( '    AcmeTest.init(argc, argv);'   + os.linesep )
        f.write( '    test();'                       + os.linesep )
        f.write( '}'                                 + os.linesep )
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

                test_defs.append( 'AcmeTest.register_subtest( %d, "%s",'
                    %  (subtest_counter,
                        test_condition.replace("\"","\\\"").replace("\'","\\\'") )
                    + line[line.find(',') + 1 :])

                dynamic_code.append( "    " +  os.linesep )
                dynamic_code.append( "    " + "# TEST: %s"%
                    test_description   + os.linesep )
                line = line.replace('TEST', 'AcmeTest.notify_result')
                line = "%s( %d, %s )" % (
                        line[:line.find('(')],
                        subtest_counter, test_condition )
                dynamic_code.append( "    "  + line + os.linesep )
                subtest_counter += 1
            else:
                dynamic_code.append( "    "  + line + os.linesep )

        f = open( test_filename, 'w' )
        #f = sys.stdout

        f.write( '#!/usr/bin/python'                     + os.linesep )
        f.write( '# -*- coding: utf-8 -*-'               + os.linesep )
        f.write( ''                                      + os.linesep )
        f.write( 'import AcmeClientPython'              + os.linesep )
        f.write( 'import AcmeTest'                      + os.linesep )
        f.write( ''                                      + os.linesep )
        f.write( 'import sys'                            + os.linesep )
        f.write( 'import os'                             + os.linesep )
        f.write( 'from optparse import OptionParser'     + os.linesep )

        f.write( ''                                      + os.linesep )
        f.write( 'def register_tests():'                 + os.linesep )
        f.write( ''                                      + os.linesep )

        for i,t in enumerate(test_defs):
            f.write( '    ' + t                          + os.linesep )
        f.write( '    pass'                              + os.linesep )
        f.write( ''                                      + os.linesep )

        f.write( 'def run_subtests():'                   + os.linesep )
        if test_type and test_type == "acme_integration_test":
            f.write( '    server, server_id, connection_state = AcmeTest.begin_acme_integration_test()' + os.linesep )
        #TODO: write something like
        #for f in (INPUT-client_lib-*):
        #    cp( f strip(f, "INPUT-client_lib-" )

        for l in dynamic_code:
            f.write( l )
        if test_type and test_type == "acme_integration_test":
            f.write( '    AcmeTest.end_acme_integration_test(server, server_id, connection_state)' + os.linesep )

        f.write( '    pass'                              + os.linesep )
        f.write( ''                                      + os.linesep )
        f.write( 'def run_tests():'                      + os.linesep )
        f.write( '    parser = OptionParser()'           + os.linesep )
        f.write( '    parser.add_option("-r", "--result-file", dest="result_file",'        + os.linesep )
        f.write( '                      help="write result file", metavar="result-file")'  + os.linesep )
        f.write( '    parser.add_option("-l", "--log-file", dest="log_file",'              + os.linesep )
        f.write( '                     help="write log to file", metavar="log_file")'      + os.linesep )
        f.write( '    parser.add_option("-b", "--acme_binary", dest="acme_binary",'           + os.linesep )
        f.write( '                     help="path to the acme binary to be used", metavar="FILE")'   + os.linesep )
        f.write( '    parser.add_option("-v", "--verbose", dest="verbose", default=False,'                  + os.linesep )
        f.write( '                      action="store_true", help="set verbosity on", metavar="verbosity")' + os.linesep )
        f.write( '    (options, args) = parser.parse_args()'                                                + os.linesep )
        f.write( '    if options.result_file: AcmeTest.set_result_file( options.result_file )'             + os.linesep )
        f.write( '    if options.log_file: AcmeTest.set_log_file( options.log_file )'                      + os.linesep )
        f.write( '    if options.acme_binary: AcmeTest.set_acme_binary( options.acme_binary )' + os.linesep )
        f.write( '    acmeTest.start_tests("%s","%s")'
                           % (document_name, test_name)  + os.linesep )
        f.write( '    register_tests()'                                  + os.linesep )
        f.write( '    ret_val = 0'                                       + os.linesep )
        f.write( '    try:'                                              + os.linesep )
        f.write( '        run_subtests()'                                + os.linesep )
        f.write( '    except Exception, ex:'                             + os.linesep )
        f.write( '        print "Error executing test"'                  + os.linesep )
        f.write( '        print ex'                                      + os.linesep )
        f.write( '        ret_val = -1'                                  + os.linesep )
        f.write( '        AcmeTest.end_client_lib()'                    + os.linesep )
        f.write( '    AcmeTest.finalize_tests()'                        + os.linesep )
        f.write( '    sys.exit(ret_val)'                                 + os.linesep )
        f.write( ''                                                      + os.linesep )
        f.write( 'if __name__ == "__main__":'                            + os.linesep )
        f.write( '    run_tests()'                                       + os.linesep )

        f.close()
    elif language == "python_acme_":
        pass

def usage(msg=''):
    if msg:
        logging.info(msg)
    logging.info('Usage: asciitest-filter -b backend -l language [ -t tabsize ]')
    logging.info('                   [ --help | -h ] [ --version | -v ] [ --type | -y ]')

def main():
    global language, backend, tabsize, test_name, document_name, test_type
    # Process command line options.
    import getopt
    opts,args = getopt.getopt(sys.argv[1:],'hvl:d:u:y:', ['help','version', 'type'])
    
    if len(args) > 0:
        logging.info( "unrecognized parameter '%s'" % args )
        usage()

    for o,v in opts:

        if o in ('--help','-h'):
            print __doc__
            sys.exit(0)
        if o in ('--version','-v'):
            print('doctest-filter version %s' % (VERSION,))
            sys.exit(0)
        if o == '-b':
            backend = v
        if o == '-d':
            document_name = v
            if(document_name.startswith("DOC")): document_name = document_name[4:]
        if o == '-u':
            test_name = v
        if o == '-l':
            v = string.lower(v)
            if v == 'c': v = 'c++'
            language = v
        if o == '-y':
            v = string.lower(v)
            test_type = v
        if o == '-t':
            try:
                tabsize = int(v)
            except:
                usage('illegal tabsize')
                sys.exit(5)
            if tabsize <= 0:
                usage('illegal tabsize')
                sys.exit(5)

#    if backend is None:
#        usage('backend option is mandatory')
#        sys.exit(4)

#    if not keywordtags.has_key(backend):
#        usage('illegal backend option')
#        sys.exit(3)

    if test_name is None:
        usage('unit-name option is mandatory')
        sys.exit(2)

    if language is None:
        usage('language option is mandatory')
        sys.exit(6)
#    if not keywords.has_key(language):
#        usage('illegal language option')
#        sys.exit(1)
    # Do the work.
    code_filter()


if __name__ == "__main__":
    logging.basicConfig(
        format='%(asctime)s %(levelname)s [%(name)s] %(message)s',
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
    # Exit with previous sys.exit() status or zero if no sys.exit().
    sys.exit(sys.exc_info()[1])

