from __future__ import annotations
from typing import List

class BuiltInType:
    VOID = 'void'
    INT = 'int'
    FLOAT = 'float'
    INT8 = 'int8'
    INT16 = 'int16'
    INT32 = 'int32'
    INT64 = 'int64'
    UINT8 = 'uint8'
    UINT16 = 'uint16'
    UINT32 = 'uint32'
    UINT64 = 'uint64'
    FLOAT32 = 'float32'
    FLOAT64 = 'float64'
    BOOL = 'bool'
    STR = 'str'
    LIST = 'List'
    TUPLE = 'Tuple'
    DICT = 'Dict'
    DICT_ITEM = 'DictItem'
    SET = 'Set'
    RANGE ='Range'
    ENUMERATE = 'enumerate'
    ZIP = 'Zip'

INT_TYPES = [BuiltInType.INT, BuiltInType.INT8, BuiltInType.INT16, BuiltInType.INT32, BuiltInType.INT64]
UINT_TYPES = [BuiltInType.UINT8, BuiltInType.UINT16, BuiltInType.UINT32, BuiltInType.UINT64]
FLOAT_TYPES = [BuiltInType.FLOAT, BuiltInType.FLOAT32, BuiltInType.FLOAT64]

VALUE_TYPES = INT_TYPES + UINT_TYPES + FLOAT_TYPES + [ BuiltInType.BOOL]

REFERENCE_TYPES = [
    BuiltInType.STR,
    BuiltInType.LIST,
    #BuiltInType.TUPLE,
    BuiltInType.DICT,
    BuiltInType.SET,
    BuiltInType.DICT_ITEM,
    BuiltInType.RANGE,
    BuiltInType.ENUMERATE,
    BuiltInType.ZIP
]

GENERIC_TYPES = [
    BuiltInType.LIST,
    BuiltInType.TUPLE,
    BuiltInType.DICT,
    BuiltInType.SET,
    BuiltInType.DICT_ITEM
]


class Type:
    def __init__(self, name='', is_class=False, genericType:Type=None, elementTypes:List[Type]=[]):
        self.name = name
        self.is_class = is_class
        self.genericType = genericType
        self.elementTypes = elementTypes
        if genericType:
            self.is_class = True
            self.name = '__'.join([genericType.name] + [x.name for x in elementTypes])

    def isClass(self):
        return self.is_class and not self.isTuple()
        
    def isTuple(self):
        return self.genericType and self.genericType.name == BuiltInType.TUPLE

    def __repr__(self):
        return self.name

def combineType(type1: Type, type2: Type) -> str:
    i_i1 = INT_TYPES.index(type1.name) if type1.name in INT_TYPES else -1
    ui_i1 = UINT_TYPES.index(type1.name) if type1.name in UINT_TYPES else -1
    i_i2 = INT_TYPES.index(type2.name) if type2.name in INT_TYPES else -1
    ui_i2 = UINT_TYPES.index(type2.name) if type2.name in UINT_TYPES else -1

    if type1.name in FLOAT_TYPES or type2.name in FLOAT_TYPES:
        if max(i_i1, ui_i1, i_i2, ui_i2) >= 2:      # int32 --> float64
            return Type(BuiltInType.FLOAT64)
        else:
            return Type(BuiltInType.FLOAT32)

    if max(i_i1, ui_i1) >= 0 and max(i_i2, ui_i2) >= 0:       
        i = max(i_i1, i_i2)
        ui = max(ui_i1, ui_i2)
        if i < 0:
            return UINT_TYPES[ui]

        i = min(3, max(i, ui + 1))
        return Type(INT_TYPES[i])

    raise Exception(f'Cannot combine type {type1.name} and {type2.name}')

def combineListTypes(types: List[Type]) -> Type:
    if types:
        type_ = types[0]
        for tp in types[1:]:
            type_ = combineType(type_, tp)

        return type_