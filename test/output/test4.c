#include <stdlib.h>
#include <string.h>
#include "types.h"

typedef struct 
{
    float64 x;
    float32 y;
} __Point__body__, *Point;

typedef struct 
{
    Point pt1;
    Point pt2;
} __Line__body__, *Line;


void Point__init__(Point self, float32 x, float32 y)
{
    self->x = x;
    self->y = y;
}

float32 Point__getX(Point self)
{
    return self->x;
}

float32 Point__getY(Point self)
{
    return self->y;
}

Point Point__add(Point self, Point pt)
{
    return ({
        Point __tmp__ = zeroalloc(sizeof(__Point__body__));
        Point__init__(__tmp__, (Point__getX(self) + pt->x), (self->y + Point__getY(pt)));
        __tmp__;
    });
}

void Line__init__(Line self, Point pt1, Point pt2)
{
    self->pt1 = pt1;
    self->pt2 = pt2;
}

Point Line__getMidPoint(Line self)
{
    return ({
        Point __tmp__ = zeroalloc(sizeof(__Point__body__));
        Point__init__(__tmp__, ((self->pt1->x + self->pt2->x) / ((double)2)), ((self->pt1->y + self->pt2->y) / ((double)2)));
        __tmp__;
    });
}

