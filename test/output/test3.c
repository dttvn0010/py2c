#include <stdlib.h>
#include <string.h>
#include "types.h"

typedef struct 
{
    int _0;
    int _1;
} Tuple__int__int ;

typedef struct 
{
    int32 _0;
    int32 _1;
} Tuple__int32__int32 ;

typedef struct 
{
    int32 _0;
    Tuple__int__int _1;
} Tuple__int32__Tuple__int__int ;


int sum(List__int lst)
{
    int32 s;
    s = 0;
    for(int __index__ = 0; __index__ < List__len(lst);__index__++)
    {
        int i = List__at(lst, __index__);
        {
            s += i;
        }
    }
    return s;
}

List__float square(List__float lst)
{
    return ({
        List__float32 __tmp__ = List__float32__empty();
        for(int __index__ = 0; __index__ < List__len(lst);__index__++)
        {
            float x = List__at(lst, __index__);
            List__append(__tmp__, (x * x));
        }
        __tmp__;
    });
}

Tuple__int__int test1()
{
    int32 i;
    int32 j;
    Tuple__int32__int32 x;
    int32 y;
    int32 z;
    i = 1;
    j = 2;
    x = (Tuple__int32__int32) {i, j};
    y = i;
    z = j;
    return (Tuple__int32__int32) {i, y};
}

void test2(Set__int x, List__int y)
{
    List__int32 lst;
    lst = ({
        List__int32 __tmp__ = List__int32__empty();
        {
            List__int __tmp__0__ = Set__toList(x);
            int __max__ = List__len(__tmp__0__);
            if(__max__ > List__len(y)) __max__ = List_len(y);
            for(int index = 0; index < __max__; index++)
            {
                int i = List__at(__tmp__0__, index);
                int j = List__at(y, index);
                List__append(__tmp__, ((index + i) + j));
            }
        }
        __tmp__;
    });
}

void test3(List__Tuple__int__int lst)
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

void test4(List__int y, Dict__int__int d)
{
    int t;
    List__int z;
    Set__int32 s;
    Dict__int__int d2;
    t = 1;
    z = ({
        int32 __tmp__[] = {1, 2, 3, 4};
        List__int32__new(__tmp__, 4);
    });
    s = ({
        int32 __tmp__[] = {1, 2, 3, 4, 5};
        Set__int32__new(__tmp__, 5);
    });
    d2 = d;
    d2 = ({
        int32 __keys__[] = {1, 3, 5};
        int32 __values__[] = {2, 4, 10};
        Dict__int32__int32__new(__keys__, __values__, 3);
    });
    List__set(z, 1, List__get(y, t, 0));
    Dict__set(d2, 2, 3);
}

