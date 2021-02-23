#include <stdlib.h>
#include <string.h>
#include "types.h"

typedef struct 
{
    int _0;
    int _1;
} Tuple__int__int ;


void test(List__Tuple__int__int lst)
{
    for(int __index__ = 0; __index__ < List__len(lst);__index__++)
    {
        int i = List__at(lst, __index__)._0;
        int j = List__at(lst, __index__)._1;
        {
            print(i, j);
        }
    }
}

