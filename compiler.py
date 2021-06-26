import ast
from node import Node, NodeType, toNode
from scope import Scope
from symbol import Symbol, SymbolKind
from codegen import CResult
from type_ import *
from typing import List

KEYWORDS = ['range', 'enumerate', 'zip', 'any', 'all', 'next', 'print']

def getType(scope: Scope, typeName: str) -> Type:
    symbol = scope.findNested(typeName)
    if symbol:
        return symbol.resolvedType
        
def getAnnotationType(scope: Scope, annotation: Node) -> Type:
    if annotation.nodeType == NodeType.NAME:
        typeName = annotation.getText()
        return getType(scope, typeName)

    elif annotation.nodeType == NodeType.TUPLE:
        tupleType = getType(scope, BuiltInType.TUPLE)
        elts = annotation.getChild('elts')
        elementTypes = [getAnnotationType(scope, elt) for elt in elts]
        return Type(genericType=tupleType, elementTypes=elementTypes)

    elif annotation.nodeType == NodeType.SUBSCRIPT:
        genericType = getType(scope, annotation.getChild('value').getText())
        slice_ = annotation.getChild('slice').getChild('value')
        
        if slice_.nodeType == NodeType.TUPLE:
            sliceElts = slice_.getChild('elts')
            elementTypes = [getAnnotationType(scope, sliceElt) for sliceElt in sliceElts]
            return Type(genericType=genericType, elementTypes=elementTypes)

        else:
            sliceType = getAnnotationType(scope, slice_)
            return Type(genericType=genericType, elementTypes=[sliceType])
        
    else:
        raise Exception('Unknown node type:' + annotation.nodeType)

def getArgumentType(node: Node, index: int) -> Type:
    annotation = node.getChild('annotation')
    if annotation:
        return getAnnotationType(node.parentScope, annotation)

    elif index == 0:
        return node.parentScope.classType
        
def getFunctionReturnType(node: Node) -> str:
    name = node.getChild('name')
    if name == '__init__':
        return Type('void')

    return_ = node.getChild('returns')
    if return_:
        if return_.nodeType == NodeType.NAME:
            typeName = return_.getText()
            return getType(node.parentScope, typeName)

        elif return_.nodeType in [NodeType.LIST, NodeType.TUPLE]:
            genericType = getType(node.parentScope, BuiltInType.TUPLE) 
            elts = return_.getChild('elts')
            elementTypes = [getType(node.parentScope, elt.getText()) for elt in elts]
            return Type(genericType=genericType, elementTypes=elementTypes)

        elif return_.nodeType == NodeType.SUBSCRIPT:
            genericType = getType(node.parentScope, return_.getChild('value').getText())
            index = return_.getChild('slice').getChild('value')
            if index.nodeType == NodeType.NAME:
                elementTypes = [getType(node.parentScope, index.getText())]
            elif index.nodeType == NodeType.TUPLE:
                elts = index.getChild('elts')
                elementTypes = [getType(node.parentScope, elt.getText()) for elt in elts]
            else:
                raise Exception('Unknown node type:' + index.nodeType)
            
            return Type(genericType=genericType, elementTypes=elementTypes)
        else:
            raise Exception('Unknown node type:' + return_.nodeType)

def getExpressionType(node: Node) -> str:
    if node.nodeType in [NodeType.NUM, NodeType.CONSTANT]:
        val = node.getText()
        if val.isdigit():
            return Type(BuiltInType.INT32)
        elif val.count('.') == 1 and val.replace('.', '').isdigit():
            return Type(BuiltInType.FLOAT64)
            
        elif val in ['True', 'False']:
            return Type(BuiltInType.BOOL)

        raise Exception('Cannot determine type for: ' , val)

    if node.nodeType in NodeType.NAME:
        name = node.getText()
        if name in KEYWORDS:
            return None

        symbol = node.parentScope.findNested(name)
        node.symbol = symbol
        return symbol.resolvedType

    if node.nodeType == NodeType.ATTR:
        var = node.getChild('value')
        resolve(var, node.parentScope)
        type_ = var.resolvedType
        genericType = type_.genericType
        typeName = type_.name
        genericTypeName = genericType.name if genericType else ''
        attr = node.getChild('attr')
        field = type_.getField(attr)
               
        if field:
            return field.type_

        elif genericTypeName == BuiltInType.LIST:
            if attr == 'get':
                return type_.elementTypes[0]

        elif genericTypeName == BuiltInType.DICT:    
            listType = getType(node.parentScope, BuiltInType.LIST)

            if attr == 'keys':
                return Type(genericType=listType, elementTypes=[type_.elementTypes[0]])

            if attr == 'values':
                return Type(genericType=listType, elementTypes=[type_.elementTypes[1]])

            if attr == 'items':
                dictItemType = getType(node.parentScope, BuiltInType.DICT_ITEM)
                dictItemType = Type(genericType=dictItemType, elementTypes=type_.elementTypes)
                return Type(genericType=listType, elementTypes=[dictItemType])

            else:
                raise Exception('Unknown attribute: ' + attr)

    if node.nodeType == NodeType.CALL:
        func = node.getChild('func')

        if func.nodeType == NodeType.NAME:
            func_name = func.getText()
            
            if func_name == 'print':
                return getType(node.parentScope, BuiltInType.VOID)

            if func_name == 'range':
                rangeType = getType(node.parentScope, BuiltInType.RANGE)
                intType = Type(BuiltInType.INT32)
                return Type(genericType=rangeType, elementTypes=[intType])

            if func_name == 'enumerate':
                args = node.getChild('args')
                assert(len(args) == 1)

                resolve(args[0], node.parentScope)

                intType = Type(BuiltInType.INT32)
                listType = getType(node.parentScope, BuiltInType.ENUMERATE)
                tupleType = getType(node.parentScope, BuiltInType.TUPLE)
                tupleType = Type(genericType=tupleType, elementTypes=[intType, args[0].resolvedType.elementTypes[0]])
                return Type(genericType=listType, elementTypes=[tupleType])

            if func_name in ['any', 'all']:
                return Type(BuiltInType.BOOL)

            if func_name == 'next':
                args = node.getChild('args')
                for arg in args:
                    resolve(arg, node.parentScope)
                
                return args[0].resolvedType.elementTypes[0]

            if func_name == 'zip':
                args = node.getChild('args')
                for arg in args:
                    resolve(arg, node.parentScope)
                
                elementTypes=[arg.resolvedType.elementTypes[0] for arg in args]

                listType = getType(node.parentScope, BuiltInType.ZIP)
                tupleType = getType(node.parentScope, BuiltInType.TUPLE)
                tupleType = Type(genericType=tupleType, elementTypes=elementTypes)
                return Type(genericType=listType, elementTypes=[tupleType])
            
            resolve(func, node.parentScope)
            return func.resolvedType
            
        elif func.nodeType == NodeType.ATTR:
            var = func.getChild('value')
            resolve(var, node.parentScope)
            attr = func.getChild('attr')
            
            if attr == 'get' and var.resolvedType.genericType and var.resolvedType.genericType.name == 'List':
                return var.resolvedType.elementTypes[0]

            symbol = node.parentScope.findNested(var.resolvedType.name + '__' + attr)
            return symbol.resolvedType
        
        else:
            raise Exception('Unknown node type: ' + func.nodeType)

    if node.nodeType == NodeType.IF_EXP:
        left = node.getChild('body').getChild('items')
        right = node.getChild('orelse').getChild('items')
        
        resolve(left, node.parentScope)
        resolve(right, node.parentScope)

        return combineType(left.resolvedType, right.resolvedType)

    if node.nodeType == NodeType.BIN_OP:
        left = node.getChild('left')
        right = node.getChild('right')
        
        resolve(left, node.parentScope)
        resolve(right, node.parentScope)

        return combineType(left.resolvedType, right.resolvedType)

    if node.nodeType == NodeType.UNARY_OP:
        operand = node.getChild('operand')
        op = node.getChild('op').nodeType
        resolve(operand, node.parentScope)
        return operand.resolvedType

    if node.nodeType in [NodeType.BOOL_OP, NodeType.COMPARE]:
        return Type(BuiltInType.BOOL)

    if node.nodeType in [NodeType.LIST, NodeType.SET]:
        genericType = getType(node.parentScope, node.nodeType)
        elts = node.getChild('elts')
        for elt in elts: 
            resolve(elt, node.parentScope)

        if elts:
            elementType = combineListTypes([elt.resolvedType for elt in elts])
            return Type(genericType=genericType, elementTypes=[elementType])

        return None

    if node.nodeType in [NodeType.LIST_COMP, NodeType.GEN_EXP]:
        generators = node.getChild('generators')
        parentScope = node.parentScope
        
        for gen in generators:
            resolve(gen, parentScope)
            parentScope = gen.scope

        elt = node.getChild('elt')
        resolve(elt, parentScope)
        listType = getType(parentScope, BuiltInType.LIST)
        return Type(genericType=listType, elementTypes=[elt.resolvedType])

    if node.nodeType == NodeType.TUPLE:
        tupleType = getType(node.parentScope, BuiltInType.TUPLE)
        elts = node.getChild('elts')
        for elt in elts: 
            resolve(elt, node.parentScope)
        
        if elts:
            return Type(genericType=tupleType, elementTypes=[elt.resolvedType for elt in elts])
            
        return None

    if node.nodeType == NodeType.DICT:
        dictType = getType(node.parentScope, BuiltInType.DICT)
        keys = node.getChild('keys')
        values = node.getChild('values')

        for k in keys:
            resolve(k, node.parentScope)

        for v in values:
            resolve(v, node.parentScope)

        if keys and values:
            keyType = combineListTypes([k.resolvedType for k in keys])
            valType = combineListTypes([v.resolvedType for v in values])
            return Type(genericType=dictType, elementTypes=[keyType, valType])

        return None

    if node.nodeType == NodeType.SUBSCRIPT:
        value = node.getChild('value')
        resolve(value, node.parentScope)

        type_ = value.resolvedType
        if type_.name in GENERIC_TYPES:
            genericType = type_
            index = node.getChild('slice').getChild('value')
            if index.nodeType == NodeType.NAME:
                resolve(index, node.parentScope)
                return Type(genericType=genericType, elementTypes=[index.resolvedType])
            elif index.nodeType == NodeType.TUPLE:
                elts = index.getChild('elts')
                for elt in elts:
                    resolve(elt, node.parentScope)
                
                return Type(genericType=genericType, elementTypes=[elt.resolvedType for elt in elts])
            elif index.nodeType == NodeType.SUBSCRIPT:
                resolve(index, node.parentScope)
                return Type(genericType=genericType, elementTypes=[index.resolvedType])
            else:
                raise Exception('Unknown node type:' + index.nodeType)
        else:
            genericType = type_.genericType
            genericTypeName = genericType.name if genericType else ''

            if genericTypeName == BuiltInType.LIST:
                if any(x in node.getChild('slice').children for x in ['lower', 'upper', 'step']):
                    return type_
                else:
                    return type_.elementTypes[0]

            if genericType == BuiltInType.DICT:
                return type_.elementTypes[1]

            if genericTypeName in [BuiltInType.TUPLE, BuiltInType.DICT_ITEM]:
                index = node.getChild('slice').getChild('value')
                if index.nodeType == NodeType.NUM:
                    n = index.getChild('n')
                    if 0 <= n < len(type_.elementTypes):
                        return type_.elementTypes[n]
                    else:
                        raise Exception('Index out of range')
                else:
                    raise Exception('Not support variable index to ' + genericTypeName)


def resolveClass(node: Node, parentScope: Scope):
    for child in node.getChildNodes():
        if child.nodeType == NodeType.CLASS:
            name = child.getChild('name')
            type_ = Type(name, True)
            symbol = Symbol(name, type_, SymbolKind.CLASS)
            child.symbol = symbol
            child.resolvedType = type_
            parentScope.define(symbol)

            scope = Scope(parentScope)
            scope.classType = type_
            child.scope = scope

def resolveFunction(node: Node, parentScope: Scope):
    for child in node.getChildNodes():
        if child.nodeType == NodeType.FUNCTION:
            child.parentScope = parentScope
            name = child.getChild('name')
            
            if parentScope.classType:
                if name != '__init__':
                    name = parentScope.classType.name + '__' + name
                else:
                    name = parentScope.classType.name + name

            type_ = getFunctionReturnType(child)
            symbol = Symbol(name, type_)
            child.symbol = symbol
            child.resolvedType = type_
            global_ = parentScope
            while global_.parent != None:
                global_ = global_.parent

            global_.define(symbol)
            
            scope = Scope(parentScope)
            scope.isFunction = True
            scope.classType = parentScope.classType
            child.scope = scope 

def resolveAssign(parentScope: Scope, target: Node, type_: Type, addVar=True):
    target.parentScope = parentScope
    target.resolvedType = type_

    if target.nodeType == NodeType.NAME:    
        name = target.getText()
        symbol = parentScope.findNested(name)
        
        if not symbol:
            symbol = Symbol(name, type_)
            parentScope.define(symbol)

        target.symbol = symbol
    
    elif target.nodeType == NodeType.TUPLE:
        elts = target.getChild('elts')
        for i, elt in enumerate(elts):
            resolveAssign(parentScope, elt, type_.elementTypes[i], addVar)

    elif target.nodeType == NodeType.ATTR:
        var_name = target.getChild('value').getText()
        var_attr = target.getChild('attr')
        tmp = target

        while tmp != None and tmp.nodeType != NodeType.FUNCTION:
            tmp = tmp.parent

        if tmp and tmp.getChild('name') == '__init__':
            args = tmp.getChild('args').getChild('args')
            if args and args[0].getChild('arg') == var_name:
                classType = tmp.parentScope.classType
                classType.addField(var_attr, type_)
               
    elif target.nodeType == NodeType.SUBSCRIPT:
        pass
    else:
        raise Exception('Unknown node type:' + target.nodeType)

def resolve(node: Node, parentScope: Scope):
    nodeType = node.nodeType
    node.parentScope = parentScope
    
    resolveClass(node, parentScope)    
    resolveFunction(node, parentScope)
    
    if nodeType in [NodeType.FUNCTION, NodeType.CLASS]:
        parentScope = node.scope

    if not node.resolvedType:
        if nodeType in [NodeType.ASSIGN, NodeType.ANN_ASSIGN]:
            value = node.getChild('value')
            resolve(value, parentScope)
            type_ = value.resolvedType
            
            if node.getChild('annotation'):
                annotation = node.getChild('annotation')
                type_ = getAnnotationType(parentScope, annotation)

            if nodeType == NodeType.ASSIGN:
                targets = node.getChild('targets')
            else:
                targets = [node.getChild('target')]

            for target in targets:
                resolveAssign(parentScope, target, type_)
               
        elif node.isExpression():            
            node.resolvedType = getExpressionType(node)
            
        elif nodeType == NodeType.WHILE:
            scope = Scope(parentScope)
            scope.isLoop = True
            parentScope = node.scope = scope 

        elif nodeType in [NodeType.FOR, NodeType.COMP]:
            scope = Scope(parentScope)
            scope.isLoop = nodeType == NodeType.FOR
            parentScope = node.scope = scope 

            target = node.getChild('target')
            iter_ = node.getChild('iter')

            resolve(iter_, parentScope)
            type_ = iter_.resolvedType
            resolveAssign(parentScope, target, type_.elementTypes[0], addVar=False)
            
        elif nodeType == NodeType.BLOCK:
            if node.parent.nodeType not in [NodeType.CLASS, NodeType.FUNCTION, NodeType.FOR, NodeType.WHILE]:
                scope = Scope(parentScope)
                parentScope = node.scope = scope 
            else:
                parentScope = node.scope = node.parent.scope

        elif nodeType == NodeType.ARGUMENTS:
            args = node.getChild('args')
            for i, arg in enumerate(args):
                arg.parentScope = parentScope
                type_ = getArgumentType(arg, i)
                name = arg.getChild('arg')
                symbol = Symbol(name, type_)
                arg.resolvedType = type_
                parentScope.define(symbol)

    for child_node in node.getChildNodes():        
        resolve(child_node, parentScope)

def replaceListComp(node: Node):
    if node.nodeType == NodeType.LIST_COMP:
        pass

    for child_node in node.getChildNodes():
        replaceListComp(child_node)

def collectTupleTypes(node: Node, tupleTypes: List[Type]):
    type_ = node.resolvedType
    genericType = type_.genericType if type_ else None
    
    if genericType and genericType.name == BuiltInType.TUPLE:
        if all(x.name != type_.name for x in tupleTypes):
            tupleTypes.append(type_)

    for child in node.getChildNodes():
        collectTupleTypes(child, tupleTypes)    

def defineTupleTypes(global_: Node):
    tupleTypes = []
    collectTupleTypes(global_, tupleTypes)

    for type_ in tupleTypes:
        symbol = Symbol(type_.name, type_)
        global_.scope.define(symbol)

class Compiler:
    def __init__(self):        
        scope = Scope()       
        global_ = Node(None, 'Global')
        global_.children['files'] = []
        global_.scope = scope
        self.global_ = global_
        self.defineNativeTypes()
        
    def defineNativeTypes(self):
        for type_ in VALUE_TYPES + REFERENCE_TYPES + [BuiltInType.VOID, BuiltInType.TUPLE]:
            is_class = type_ in REFERENCE_TYPES
            symbol = Symbol(type_, Type(type_, is_class))
            self.global_.scope.define(symbol)

    def addInput(self, src: str):
        global_ = self.global_
        node = toNode(global_, ast.parse(src))
        
        global_.children['files'].append(node)

        replaceListComp(global_)

        resolve(global_, global_.scope)

        defineTupleTypes(global_)

        #print(global_)

    def cppEmit(self) -> str:
        result = CResult()

        for file in self.global_.getChildNodes():
            result.emitDefinition(file)

        for file in self.global_.getChildNodes():            
            result.emitImplement(file)

        return result.code
        