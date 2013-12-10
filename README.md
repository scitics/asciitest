asciitest - create automated test from your documentation
=========================================================

Use example code snipptes from your asciidoc documentation for automated testing
and be sure all your examples are working and up to date and save the time
writing separate tests.

example
-------

Write a minimalistic example script with just the essence you want to 
demonstrate and let asciitest create fully working scripts for you.

```
["asciitest", "example_test", "python"]
code~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import math
s = math.sin(0)
TEST(s == 0, 'sin(0) should be zero' )
s = math.sin(math.pi/2)
TEST(s == 1, 'sin(0) should be one' )
code~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
```
 
how to use
----------
Create your documentation using asciidoc, prepare some environmental 
configuration and have ready to run and up to date tests every time you build
your project

wish list
---------
* syntax highlighting for generated code
* support multi line TEST() calls
* provide cmake helper scripts for generating the documentation
* support more languages
* support python inline examples like doctest does

