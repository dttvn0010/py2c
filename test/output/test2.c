#include <stdlib.h>
#include <string.h>
#include "types.h"


float max1(float x, float y)
{
    float __ret__;
    bool __is_return__ = FALSE;
    __ret__ = ((x > y)? (x) : (y));
    __Scope_0__end__:
    return __ret__;
}

float max2(float x, float y)
{
    float __ret__;
    bool __is_return__ = FALSE;
    if(x > y)
    {
        __ret__ = x;
        __is_return__ = TRUE;
        goto __Scope_1__end__;
    }
    else
    {
        __ret__ = y;
        __is_return__ = TRUE;
        goto __Scope_1__end__;
    }
    __Scope_1__end__:
    return __ret__;
}

float max3(float x, float y, float z)
{
    float __ret__;
    bool __is_return__ = FALSE;
    if(y <= x && x >= z)
    {
        __ret__ = x;
        __is_return__ = TRUE;
        goto __Scope_2__end__;
    }
    else if(x <= y && y >= z)
    {
        __ret__ = y;
        __is_return__ = TRUE;
        goto __Scope_2__end__;
    }
    else
    {
        __ret__ = z;
        __is_return__ = TRUE;
        goto __Scope_2__end__;
    }
    __Scope_2__end__:
    return __ret__;
}

