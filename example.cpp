#include <stdio.h>

int main(int argn, char **)
{
#   ifdef NDEBUG
    printf("RELEASE hello world\n");
#   else
    printf("DEBUG hello world\n");
#endif
    fflush(stdout);

    // return with failure if arguments exist
    return argn == 1? 0:-1;
}
