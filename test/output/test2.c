#include <stdlib.h>
#include <string.h>
#include "types.h"


float max1(float x, float y)
{
    return ((x > y)? (x) : (y));
}

float max2(float x, float y)
{
    if(x > y)
    {
        return x;
    }
    else
    {
        return y;
    }
}

float max3(float x, float y, float z)
{
    if(y <= x && x >= z)
    {
        return x;
    }
    else if(x <= y && y >= z)
    {
        return y;
    }
    else
    {
        return z;
    }
}

