#ifndef __TYPE_H__
#define __TYPE_H__
#include <stdlib.h>
#include <string.h>

typedef char int8;
typedef short int16;
typedef int int32;
typedef long long int64;

typedef unsigned char uint8;
typedef unsigned short uint16;
typedef unsigned int uint32;
typedef unsigned long long uint64;

typedef float float32;
typedef double float64;

#define zeroalloc(sz) ({                \
    void* ptr = malloc(sz);             \
    memset(ptr, 0, sz);                 \
    ptr;                                \
})

#define DECLARE_LIST(list_type, type)   \
    typedef struct {                    \
        type* data;                     \
        int* p_size;                    \
        int* p_capacity;                \
    }__##list_type##__body__, * list_type;

DECLARE_LIST(List__int, int);
DECLARE_LIST(List__float, float);

DECLARE_LIST(List__int32, int32);
DECLARE_LIST(List__float32, float32);

#define List__len(lst)  (*((lst)->p_size))
#define List__at(lst, i)  (*((lst)->data + i))

#define List__empty(type) ({                                        \
    int sz = sizeof(__List__##type##__body__);                      \
    List__##type tmp = zeroalloc(sz) ;                              \
    tmp;                                                            \
})

#define List__append(lst, i) {}

#endif