#include <stdlib.h>
#include <string.h>
#include "types.h"

typedef struct 
{
    int x;
    int y;
    int __ref_count__;
} __Point__body__;

typedef struct 
{
    __Point__body__* __body__;
    bool __ref_hold__;
} Point;

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


void print(int s)
{
    bool __is_return__ = FALSE;
    int s = 0;
}

void Point__init__(Point self, int x, int y)
{
    bool __is_return__ = FALSE;
    Point self;
    int x = 0;
    int y = 0;
    self.__body__->x = x;
    self.__body__->y = y;
    release_ref(self);
}

int testFor1(int N)
{
    int __ret__;
    bool __is_return__ = FALSE;
    int N = 0;
    int32 s = 0;
    s = 0;
    for(int i = 0; i < N; i += 1)
    {
        bool __is_break__ = FALSE, __is_continue__ = FALSE;
        int32 i = 0;
        s += i;
        if(__is_break__) break;
    }
    {
        int i = 0;
        while(1)
        {
            if(i < N)
            {
                bool __is_break__ = FALSE, __is_continue__ = FALSE;
                int32 i = 0;
                s += i;
                if(i > 100)
                {
                    Point tmp;
                    tmp = ({
                        Point __self__;
                        __self__.__body__ = zeroalloc(sizeof(__Point__body__));
                        __self__.__body__->__ref_count__ = 1;
                        __self__.__ref_hold__ = TRUE;
                        Point__init__(__self__, 0, 0);
                        __self__;
                    });
                    if(i > 200)
                    {
                        Point tmp2;
                        tmp2 = ({
                            Point __self__;
                            __self__.__body__ = zeroalloc(sizeof(__Point__body__));
                            __self__.__body__->__ref_count__ = 1;
                            __self__.__ref_hold__ = TRUE;
                            Point__init__(__self__, 1, 2);
                            __self__;
                        });
                        if(i > 300)
                        {
                            __is_break__ = TRUE;
                            goto __Scope_2_1_0_0__end__;
                        }
                        __Scope_2_1_0_0__end__:
                        release_ref(tmp2);
                        if(__is_break__ || __is_continue__) goto __Scope_2_1_0__end__;
                    }
                    __Scope_2_1_0__end__:
                    release_ref(tmp);
                    if(__is_break__ || __is_continue__) goto __Scope_2_1__end__;
                }
                print(s);
                __Scope_2_1__end__:
                if(__is_break__) break;
            }
            else
            {
                int32 i = 0;
                s += N;
                break;
            }
            i += 1;
        }
    }
    __ret__ = s;
    __Scope_2__end__:
    return __ret__;
}

int testFor2(List__int lst)
{
    int __ret__;
    bool __is_return__ = FALSE;
    List__int lst;
    int32 s = 0;
    s = 0;
    for(int __index__ = 0; __index__ < List__len(lst);__index__++)
    {
        int i = List__at(lst, __index__);
        bool __is_break__ = FALSE, __is_continue__ = FALSE;
        int i = 0;
        s += i;
        if(__is_break__) break;
    }
    {
        int __index__ = 0;
        while(1)
        {
            if(__index__ < List__len(lst))
            {
                int i = List__at(lst, __index__);
                bool __is_break__ = FALSE, __is_continue__ = FALSE;
                int i = 0;
                s += i;
                if(i > 100)
                {
                    __is_continue__ = TRUE;
                    goto __Scope_3_1__end__;
                }
                print(s);
                __Scope_3_1__end__:
                if(__is_break__) break;
            }
            else
            {
                int i = 0;
                s *= 2;
                break;
            }
             __index__ ++; 
        }
    }
    __ret__ = s;
    __Scope_3__end__:
    release_ref(lst);
    return __ret__;
}

List__float square(List__float lst)
{
    List__float __ret__;
    bool __is_return__ = FALSE;
    List__float lst;
    __ret__ = ({
        List__float32 __tmp__ = List__float32__empty();
        for(int __index__ = 0; __index__ < List__len(lst);__index__++)
        {
            float x = List__at(lst, __index__);
            List__append(__tmp__, (x * x));
        }
        __tmp__;
    });
    __Scope_4__end__:
    release_ref(lst);
    return __ret__;
}

Tuple__int__int test1()
{
    Tuple__int__int __ret__;
    bool __is_return__ = FALSE;
    int32 i = 0;
    int32 j = 0;
    Tuple__int32__int32 x;
    int32 y = 0;
    int32 z = 0;
    i = 1;
    j = 2;
    x = (Tuple__int32__int32) {i, j};
    y = i;
    z = j;
    __ret__ = (Tuple__int32__int32) {i, y};
    __Scope_5__end__:
    return __ret__;
}

void test2(Set__int x, List__int y)
{
    bool __is_return__ = FALSE;
    Set__int x;
    List__int y;
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
    release_ref(x);
    release_ref(y);
    release_ref(lst);
}

void test3(List__Tuple__int__int lst)
{
    bool __is_return__ = FALSE;
    List__Tuple__int__int lst;
    for(int __index__ = 0; __index__ < List__len(lst);__index__++)
    {
        int i = List__at(lst, __index__)._0;
        int j = List__at(lst, __index__)._1;
        bool __is_break__ = FALSE, __is_continue__ = FALSE;
        int i = 0;
        int j = 0;
        print(i, j);
        if(__is_break__) break;
    }
    release_ref(lst);
}

void test4(List__int y, Dict__int__int d)
{
    bool __is_return__ = FALSE;
    List__int y;
    Dict__int__int d;
    int t = 0;
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
    inc_ref(d2);
    release_ref(d2);
    d2 = ({
        int32 __keys__[] = {1, 3, 5};
        int32 __values__[] = {2, 4, 10};
        Dict__int32__int32__new(__keys__, __values__, 3);
    });
    List__set(z, 1, List__get(y, t, 0));
    Dict__set(d2, 2, 3);
    release_ref(y);
    release_ref(d);
    release_ref(z);
    release_ref(s);
    release_ref(d2);
}

