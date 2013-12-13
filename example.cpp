#include <stdio.h>

int main(int argn, char **)
{
    printf("hello world\n");
    fflush(stdout);

    // return with failure if arguments exist
    return argn == 1? 0:-1;
}
