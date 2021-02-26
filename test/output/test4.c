#include <stdlib.h>
#include <string.h>
#include "types.h"

typedef struct 
{
    float32 x;
    float32 y;
    int __ref_count__;
} __Point__body__;

typedef struct 
{
    __Point__body__* __body__;
    bool __ref_hold__;
} Point;

typedef struct 
{
    Point pt1;
    Point pt2;
    int __ref_count__;
} __Line__body__;

typedef struct 
{
    __Line__body__* __body__;
    bool __ref_hold__;
} Line;


void Point__init__(Point self, float32 x, float32 y)
{
    bool __is_return__ = FALSE;
    self.__body__->x = x;
    self.__body__->y = y;
}

float32 Point__getX(Point self)
{
    float32 __ret__;
    bool __is_return__ = FALSE;
    __ret__ = self.__body__->x;
    __Scope_0_1__end__:
    return __ret__;
}

float32 Point__getY(Point self)
{
    float32 __ret__;
    bool __is_return__ = FALSE;
    __ret__ = self.__body__->y;
    __Scope_0_2__end__:
    return __ret__;
}

Point Point__add(Point self, Point pt)
{
    Point __ret__;
    bool __is_return__ = FALSE;
    __ret__ = ({
        float32  __arg__0__ = (Point__getX(self) + pt.__body__->x);
        float32  __arg__1__ = (self.__body__->y + Point__getY(pt));
        Point __self__;
        __self__.__body__ = zeroalloc(sizeof(__Point__body__));
        __self__.__body__->__ref_count__ = 1;
        __self__.__ref_hold__ = TRUE;
        Point__init__(__self__,  __arg__0__,  __arg__1__);
        __self__;
    });
    __Scope_0_3__end__:
    return __ret__;
}

void Line__init__(Line self, Point pt1, Point pt2)
{
    bool __is_return__ = FALSE;
    release_ref(self.__body__->pt1);
    self.__body__->pt1 = pt1;
    inc_ref(self.__body__->pt1);
    release_ref(self.__body__->pt2);
    self.__body__->pt2 = pt2;
    inc_ref(self.__body__->pt2);
}

Point Line__getMidPoint(Line self)
{
    Point __ret__;
    bool __is_return__ = FALSE;
    __ret__ = ({
        float64  __arg__0__ = ((self.__body__->pt1.__body__->x + self.__body__->pt2.__body__->x) / ((double)2));
        float64  __arg__1__ = ((self.__body__->pt1.__body__->y + self.__body__->pt2.__body__->y) / ((double)2));
        Point __self__;
        __self__.__body__ = zeroalloc(sizeof(__Point__body__));
        __self__.__body__->__ref_count__ = 1;
        __self__.__ref_hold__ = TRUE;
        Point__init__(__self__,  __arg__0__,  __arg__1__);
        __self__;
    });
    __Scope_1_1__end__:
    return __ret__;
}

void Line__setPoint1(Line self, float x1, float y1)
{
    bool __is_return__ = FALSE;
    release_ref(self.__body__->pt1);
    self.__body__->pt1 = ({
        Point __self__;
        __self__.__body__ = zeroalloc(sizeof(__Point__body__));
        __self__.__body__->__ref_count__ = 1;
        __self__.__ref_hold__ = TRUE;
        Point__init__(__self__, x1, y1);
        __self__;
    });
}

void Line__setPoint2(Line self, Point pt)
{
    bool __is_return__ = FALSE;
    release_ref(self.__body__->pt2);
    self.__body__->pt2 = pt;
    inc_ref(self.__body__->pt2);
}

Line newLine(float32 x1, float32 y1, float32 x2, float32 y2)
{
    Line __ret__;
    bool __is_return__ = FALSE;
    Point pt1;
    Point pt2;
    Line line;
    pt1 = ({
        Point __self__;
        __self__.__body__ = zeroalloc(sizeof(__Point__body__));
        __self__.__body__->__ref_count__ = 1;
        __self__.__ref_hold__ = TRUE;
        Point__init__(__self__, x1, y1);
        __self__;
    });
    pt2 = ({
        Point __self__;
        __self__.__body__ = zeroalloc(sizeof(__Point__body__));
        __self__.__body__->__ref_count__ = 1;
        __self__.__ref_hold__ = TRUE;
        Point__init__(__self__, x2, y2);
        __self__;
    });
    line = ({
        Line __self__;
        __self__.__body__ = zeroalloc(sizeof(__Line__body__));
        __self__.__body__->__ref_count__ = 1;
        __self__.__ref_hold__ = TRUE;
        Line__init__(__self__, pt1, pt2);
        __self__;
    });
    __ret__ = line;
    inc_ref(line);
    __Scope_2__end__:
    release_ref(pt1);
    release_ref(pt2);
    release_ref(line);
    return __ret__;
}

Point newPoint(float32 x, float32 y)
{
    Point __ret__;
    bool __is_return__ = FALSE;
    if(x > 0)
    {
        Point tmp0;
        tmp0 = ({
            Point __self__;
            __self__.__body__ = zeroalloc(sizeof(__Point__body__));
            __self__.__body__->__ref_count__ = 1;
            __self__.__ref_hold__ = TRUE;
            Point__init__(__self__, 0.0, 0.0);
            __self__;
        });
        if(y > 0)
        {
            Point tmp1;
            tmp1 = ({
                Point __self__;
                __self__.__body__ = zeroalloc(sizeof(__Point__body__));
                __self__.__body__->__ref_count__ = 1;
                __self__.__ref_hold__ = TRUE;
                Point__init__(__self__, x, y);
                __self__;
            });
            __ret__ = tmp1;
            inc_ref(tmp1);
            __is_return__ = TRUE;
            __Scope_3_0_0__end__:
            release_ref(tmp1);
            if(__is_return__) goto __Scope_3_0__end__;
        }
        else
        {
            Point tmp2;
            tmp2 = ({
                float32  __arg__1__ = -y;
                Point __self__;
                __self__.__body__ = zeroalloc(sizeof(__Point__body__));
                __self__.__body__->__ref_count__ = 1;
                __self__.__ref_hold__ = TRUE;
                Point__init__(__self__, x,  __arg__1__);
                __self__;
            });
            if(x > 1)
            {
                __ret__ = tmp2;
                inc_ref(tmp2);
                __is_return__ = TRUE;
                goto __Scope_3_0_1__end__;
            }
            x = 1;
            __Scope_3_0_1__end__:
            release_ref(tmp2);
            if(__is_return__) goto __Scope_3_0__end__;
        }
        __Scope_3_0__end__:
        release_ref(tmp0);
        if(__is_return__) goto __Scope_3__end__;
    }
    else
    {
        Point tmp3;
        tmp3 = ({
            float32  __arg__0__ = -x;
            Point __self__;
            __self__.__body__ = zeroalloc(sizeof(__Point__body__));
            __self__.__body__->__ref_count__ = 1;
            __self__.__ref_hold__ = TRUE;
            Point__init__(__self__,  __arg__0__, y);
            __self__;
        });
        __ret__ = tmp3;
        inc_ref(tmp3);
        __is_return__ = TRUE;
        __Scope_3_1__end__:
        release_ref(tmp3);
        if(__is_return__) goto __Scope_3__end__;
    }
    __Scope_3__end__:
    return __ret__;
}

void print(float32 x, float32 y)
{
    bool __is_return__ = FALSE;
}

void testPoint(Point pt)
{
    bool __is_return__ = FALSE;
    print(pt.__body__->x, pt.__body__->y);
}

Line test()
{
    Line __ret__;
    bool __is_return__ = FALSE;
    Line line;
    Point pt;
    line = newLine(0.0, 1.0, 1.0, 0.0);
    Line__setPoint1(line, 1.0, 2.0);
    testPoint(line.__body__->pt1);
    testPoint(line.__body__->pt2);
    pt = ({
        Point __self__;
        __self__.__body__ = zeroalloc(sizeof(__Point__body__));
        __self__.__body__->__ref_count__ = 1;
        __self__.__ref_hold__ = TRUE;
        Point__init__(__self__, 0.0, 0.0);
        __self__;
    });
    testPoint(pt);
    {
        Point  __arg__0__ = ({
            Point __self__;
            __self__.__body__ = zeroalloc(sizeof(__Point__body__));
            __self__.__body__->__ref_count__ = 1;
            __self__.__ref_hold__ = TRUE;
            Point__init__(__self__, 1.0, 1.0);
            __self__;
        });
        testPoint( __arg__0__);
        release_ref( __arg__0__);
    };
    {
        Point  __arg__0__ = newPoint(0.0, 1.0);
        testPoint( __arg__0__);
        release_ref( __arg__0__);
    };
    Line__setPoint2(line, pt);
    __ret__ = line;
    inc_ref(line);
    __Scope_6__end__:
    release_ref(line);
    release_ref(pt);
    return __ret__;
}

