from __future__ import annotations
from typing import List
from node import Node, NodeType
from symbol import Symbol
from type_ import BuiltInType, VALUE_TYPES, REFERENCE_TYPES, combineListTypes

op_signs = {
    'Add': '+',
    'Sub': '-',
    'Mult': '*',
    #'Pow': '**'
    'Div': '/',
    'FloorDiv': '/',
    'Mod': '%',
    'And': '&&',
    'Or': '||',
    'Not': '!',
    'BitAnd': '&',
    'BitOr': '|',
    'BitXor': '^',
    'Invert': '~',
    'UAdd': '+',
    'USub': '-',
    'Gt': '>',
    'GtE': '>=',
    'Lt': '<',
    'LtE': '<=',
    'NotEq': '!=',
    'Eq': '=='
    #''
}

def get_sign(node: Node) -> int:
    if node.nodeType == NodeType.VALUE:
        val = node.value
    elif node.nodeType == NodeType.NUM:
        val = node.getChild('n')
    else:
        return None
   
    try:
        x = float(val)
        if x >= 0:
            return 1
        else:
            return -1
    except:
        pass

class CResult:
    def __init__(self):
        self.code = ''
        self.headerName = ''
        self.indent = 0
        self.hasStrings = False
        self.previousNode: Node = None
        self.nextStringLiteral = 0

    def append(self, st) -> CResult:
        self.code += str(st)
        return self

    def emitIndent(self) -> CResult:
        self.append("    " * self.indent)
        return self

    def emitNewline(self) -> CResult:
        self.append('\n')
        return self

    def emitSubscript(self, node: Node):
        value = node.getChild('value')
        slice_ = node.getChild('slice')
        type_ = value.resolvedType
        genericType = type_.genericType
        
        if genericType and genericType.name in ['Set']:
            raise Exception('Cannot index to ' + genericType.name)

        typeName = genericType.name if genericType else type_.name

        if slice_.getChild('value'):
            index = slice_.getChild('value')
            indexText = str(index.getText())

            if typeName == BuiltInType.DICT_ITEM:
                self.emitExpression(value).append('->').append({'0': 'key', '1': 'value'}[indexText])

            elif typeName == BuiltInType.TUPLE:
                if indexText.isdigit():
                    indexNum = int(indexText)
                    if 0 <= indexNum < len(type_.elementTypes):
                        self.emitExpression(value).append(f'._{indexNum}')
                    else:
                        raise Exception('Index out of range')
                else:
                    raise Exception('Not support variable index to Tuple')
            else:
                self.append(f'{typeName}__at(').emitExpression(value).append(', ').emitExpression(index).append(')')
        else:
            lower = slice_.getChild('lower')
            upper = slice_.getChild('upper')
            step = slice_.getChild('step') or Node.valueNode(1)

            if lower and upper:
                self.append(f'{typeName}__range__(').emitExpression(value).append(', ')
                self.emitExpression(lower).append(', ')
                self.emitExpression(upper).append(', ')
                self.emitExpression(step).append(')')

            elif not lower and upper:
                self.append(f'{typeName}__range__left__(').emitExpression(value).append(', ')
                self.emitExpression(upper).append(', ')
                self.emitExpression(step).append(')')
            
            elif not upper and lower:
                self.append(f'{typeName}__range__right__(').emitExpression(value).append(', ')
                self.emitExpression(lower).append(', ')
                self.emitExpression(step).append(')')
                
            else:
                self.append(f'{typeName}__range__by_step__(').emitExpression(value).append(', ')
                self.emitExpression(step).append(')')

    def emitIfExp(self, node):
        test = node.getChild('test')
        left = node.getChild('body').getChild('items')
        right = node.getChild('orelse').getChild('items')
        self.append('(')
        self.emitExpression(test, forceBracket=True)
        self.append('? ').emitExpression(left, forceBracket=True)
        self.append(' : ').emitExpression(right, forceBracket=True)
        self.append(')')

    def emitBinary(self, node: Node):
        op = node.getChild('op').nodeType
        
        self.append('(')
        self.emitExpression(node.getChild('left'))        
        self.append(f' {(op_signs[op])} ')

        if op == 'Div':
            self.append('((double)')

        self.emitExpression(node.getChild('right'))

        if op == 'Div':
            self.append(')')

        self.append(')')
    
    def emitUnary(self, node):
        op = node.getChild('op').nodeType
        self.append(op_signs[op])
        self.emitExpression(node.getChild('operand'))
        
    def emitBool(self, node: Node):
        op = node.getChild('op').nodeType
        values = node.getChild('values')
        self.append('(')

        for i, value in enumerate(values):
            self.emitExpression(value)
            if i+1 < len(values):
                self.append(f' {op_signs[op]} ')

        self.append(')')
        
    def emitCompare(self, node: Node):
        left = node.getChild('left')
        ops = node.getChild('ops')
        comparators = node.getChild('comparators')
        self.append('(')

        for i, op in enumerate(ops):
            self.emitExpression(left if i == 0 else comparators[i-1])
            self.append(f' {op_signs[op.nodeType]} ')
            self.emitExpression(comparators[i])
            if i+1 < len(ops):
                self.append(' && ')

        self.append(')')

    def emitAny(self, node: Node):
        args = node.getChild('args')
        assert(len(args) == 1 and args[0].nodeType == NodeType.GEN_EXP)
        generators = args[0].getChild('generators')

        self.append('({\n')
        self.indent += 1

        self.emitIndent().append('bool __tmp__ = FALSE;\n')

        def emitBody():
            self.emitIndent().append(f'if')
            self.emitExpression(args[0].getChild('elt'), forceBracket=True)
            self.append('{ __tmp__ = TRUE; break; }\n')

        def emitGen(i):
            emitBody_ = emitBody if i+1 == len(generators) else lambda : emitGen(i+1)
            self.emitFor(generators[i], emitBody=emitBody_)
            
        emitGen(0)

        self.emitIndent().append('__tmp__;\n')

        self.indent -= 1
        self.emitIndent().append('})')

    def emitAll(self, node: Node):
        args = node.getChild('args')
        assert(len(args) == 1 and args[0].nodeType == NodeType.GEN_EXP)
        generators = args[0].getChild('generators')

        self.append('({\n')
        self.indent += 1

        self.emitIndent().append('bool __tmp__ = TRUE;\n')

        def emitBody():
            self.emitIndent().append(f'if(!')
            self.emitExpression(args[0].getChild('elt')).append(')')
            self.append('{ __tmp__ = FALSE; break; }\n')

        def emitGen(i):
            emitBody_ = emitBody if i+1 == len(generators) else lambda : emitGen(i+1)
            self.emitFor(generators[i], emitBody=emitBody_)
            
        emitGen(0)

        self.emitIndent().append('__tmp__;\n')

        self.indent -= 1
        self.emitIndent().append('})')

    def emitNext(self, node: Node):
        args = node.getChild('args')
        assert(len(args) == 2 and args[0].nodeType == NodeType.GEN_EXP)
        elementTypeName = args[0].resolvedType.elementTypes[0].name
        generators = args[0].getChild('generators')

        self.append('({\n')
        self.indent += 1

        self.emitIndent().append(f'{elementTypeName} __tmp__ = ').emitExpression(args[1]).append(';\n')

        def emitBody():
            self.emitIndent().append('{ __tmp__ = ').emitExpression(args[0].getChild('elt'))
            self.append('; break; }\n')

        def emitGen(i):
            emitBody_ = emitBody if i+1 == len(generators) else lambda : emitGen(i+1)
            self.emitFor(generators[i], emitBody=emitBody_)
            
        emitGen(0)

        self.emitIndent().append('__tmp__;\n')

        self.indent -= 1
        self.emitIndent().append('})')

    def emitCall(self, node: Node) :
        func = node.getChild('func')
        args = node.getChild('args')
        isConstructor = False
        className = ''

        if func.nodeType == NodeType.NAME:
            func_name = func.getText()
            if func.symbol and func.symbol.isClass:
                className = func_name
                func_name = func_name + '__init__'
                isConstructor = True

        elif func.nodeType == NodeType.ATTR:
            var = func.getChild('value')
            type_ = var.resolvedType
            typeName = type_.genericType.name if type_.genericType else type_.name
            attr = func.getChild('attr')
            func_name = f'{typeName}__{attr}'
        else:
            raise Exception('Unknown node type:' + func.nodeType)
        
        if func_name == 'any':
            return self.emitAny(node)

        if func_name == 'all':
            return self.emitAll(node)

        if func_name == 'next':
            return self.emitNext(node)

        if not isConstructor:
            if func_name in VALUE_TYPES:
                self.append(f'({func_name})')
            elif func_name == 'str' and args:
                self.append(args[0].symbol.resolvedType.name + '__to_str')
            else:
                self.append(func_name)

            self.append('(')
            if func.nodeType == NodeType.ATTR:
                self.append(func.getChild('value').getChild('id'))
                if args: self.append(', ')
             
            self.emitExpressionChain(args)            
            self.append(')')
        else:
            self.append('({\n')
            self.indent += 1
            self.emitIndent().append(f'{className} __tmp__ = zeroalloc(sizeof(__{className}__body__));\n')
            self.emitIndent().append(func_name + '(__tmp__')
            if args: self.append(', ')
            self.emitExpressionChain(args)
            self.append(');\n')
            self.emitIndent().append('__tmp__;\n')
            self.indent -= 1
            self.emitIndent().append('})')

    def emitTuple(self, node: Node) :
        type_ = node.resolvedType
        elts = node.getChild('elts')        
        self.append(f'({type_.name}) {{')
        self.emitExpressionChain(elts)        
        self.append('}')

    def emitListSet(self, node: Node):    
        type_ = node.resolvedType
        genericTypeName = type_.genericType.name
        elementTypeName = type_.elementTypes[0].name
        elts = node.getChild('elts')
        N = len(elts)
        
        self.append('({\n')
        self.indent += 1
        
        self.emitIndent().append(f'{elementTypeName} __tmp__[] = {{')
        self.emitExpressionChain(elts).append('};\n')

        self.emitIndent().append(f'{genericTypeName}__{elementTypeName}__new(__tmp__, {N});\n')

        self.indent -= 1
        self.emitIndent().append('})')                

    def emitListComp(self, node: Node):
        elementTypeName = node.resolvedType.elementTypes[0].name
        generators = node.getChild('generators')

        self.append('({\n')
        self.indent += 1

        self.emitIndent().append(f'List__{elementTypeName} __tmp__ = List__{elementTypeName}__empty();\n')
        
        def emitBody():
            self.emitIndent().append(f'List__append(__tmp__, ')
            self.emitExpression(node.getChild('elt')).append(');\n')

        def emitGen(i):
            emitBody_ = emitBody if i+1 == len(generators) else lambda : emitGen(i+1)
            self.emitFor(generators[i], emitBody=emitBody_)
            
        emitGen(0)

        self.emitIndent().append('__tmp__;\n')

        self.indent -= 1
        self.emitIndent().append('})')

    def emitDict(self, node: Node):
        keys = node.getChild('keys')
        values = node.getChild('values')

        type_ = node.resolvedType
        keyTypeName = type_.elementTypes[0].name
        valueTypeName = type_.elementTypes[0].name        
        dictTypeName = type_.name

        N = len(keys)
        self.append('({\n')
        self.indent += 1

        self.emitIndent().append(f'{keyTypeName} __keys__[] = {{')
        self.emitExpressionChain(keys).append('};\n')

        self.emitIndent().append(f'{valueTypeName} __values__[] = {{')
        self.emitExpressionChain(values).append('};\n')

        self.emitIndent().append(f'{dictTypeName}__new(__keys__, __values__, {N});\n')

        self.indent -= 1
        self.emitIndent().append('})')                

    def emitExpression(self, node: Node, forceBracket=False) -> CResult:
        if not node:
            return self

        if node.nodeType in [NodeType.VALUE, NodeType.NUM, NodeType.NAME, NodeType.ATTR]:
            if forceBracket: self.append('(')
            self.append(node.getText())
            if forceBracket: self.append(')')
            
        elif node.nodeType == NodeType.SUBSCRIPT:
            if forceBracket: self.append('(')
            self.emitSubscript(node)
            if forceBracket: self.append(')')

        elif node.nodeType == NodeType.IF_EXP:
            self.emitIfExp(node)

        elif node.nodeType == NodeType.BIN_OP:
            self.emitBinary(node)

        elif node.nodeType == NodeType.UNARY_OP:
            self.emitUnary(node)

        elif node.nodeType == NodeType.BOOL_OP:
            self.emitBool(node)

        elif node.nodeType == NodeType.COMPARE:
            self.emitCompare(node)

        elif node.nodeType == NodeType.CALL:
            if forceBracket: self.append('(')
            self.emitCall(node)
            if forceBracket: self.append(')')

        elif node.nodeType == NodeType.TUPLE:
            self.emitTuple(node)

        elif node.nodeType in [NodeType.LIST, NodeType.SET]:
            self.emitListSet(node)

        elif node.nodeType == NodeType.LIST_COMP:
            self.emitListComp(node)

        elif node.nodeType == NodeType.DICT:
            self.emitDict(node)

        return self

    def emitExpressionChain(self, nodes: List[Node]) -> CResult:
        for i, node in enumerate(nodes):
            self.emitExpression(node)
            if i+1 < len(nodes):
                self.append(', ')

        return self

    def emitVariable(self, variable:Node):        
        self.emitIndent()
        self.append(variable.type_.name).append(' ').append(variable.name).append(';\n')

    def emitClass(self, node: Node):
        className = node.getChild('name')
        items = node.getChild('body').getChild('items')
        for item in items:
            if item.nodeType == NodeType.FUNCTION:
                self.emitFunction(item)

    def emitFunction(self, node: Node):
        returnType = node.resolvedType
        args = node.getChild('args')
        args = args.getChild('args')
        symbol = node.symbol
        
        self.append(returnType.name if returnType else 'void')
        self.append(' ')        
        self.append(symbol.name)
        self.append('(')
        
        for i, arg in enumerate(args):
            self.append(arg.resolvedType.name).append(' ')
            self.append(arg.getChild('arg'))
            if i + 1 < len(args):
                self.append(", ")
            
        self.append(")\n")

        self.emitBlock(node.getChild('body'))
        self.append('\n')
            
    def emitAssign(self, target: Node, value: Node):
        if target.nodeType == NodeType.TUPLE:
            targetElts = target.getChild('elts')

            if value.nodeType == NodeType.TUPLE:
                valueElts = value.getChild('elts')
                assert(len(targetElts) == len(valueElts))

                for targetElt, valueElt in zip(targetElts, valueElts):
                    self.emitAssign(targetElt, valueElt)
            
            else:                
                self.emitIndent().append('{')
                self.indent += 1
                self.emitIndent().append(value.resolvedType.name).append(' __tmp__ = ')
                self.emitExpression(value).append(';\n')

                for i, targetElt in enumerate(targetElts):
                    self.emitIndent().append(targetElt.getText()).append(f' = __tmp__._{i};\n')

                self.indent -= 1
                self.emitIndent().append('}\n')

        elif target.nodeType in [NodeType.NAME, NodeType.ATTR]:
            self.emitIndent().append(target.getText()).append(' = ').emitExpression(value).append(';\n')
        
        elif target.nodeType == NodeType.SUBSCRIPT:
            index = target.getChild('slice').getChild('value')
            target = target.getChild('value')
            type_ = target.resolvedType
            genericTypeName = type_.genericType.name            
            self.emitIndent().append(genericTypeName).append('__set(')
            self.emitExpression(target).append(', ').emitExpression(index)
            self.append(', ').emitExpression(value)
            self.append(');\n')
        else:
            raise Exception('Unknown node type:' + target.nodeType)

    def emitAugAssign(self, node: Node):
        self.emitIndent()
        target = node.getChild('target')
        op = op_signs[node.getChild('op').nodeType]
        
        if target.nodeType in [NodeType.NAME, NodeType.ATTR]:
            self.append(target.getText())
        else:
            raise Exception('Unknown node type:' + target.nodeType)
        
        self.append(' ').append(op).append('=').append(' ')
        self.emitExpression(node.getChild('value')).append(';\n')

    def emitReturn(self, node: Node):
        self.emitIndent()
        value = node.getChild('value')
        self.append("return ").emitExpression(value).append(";\n")

    def emitIf(self, node, indent=True):
        if indent: 
            self.emitIndent()
        
        self.append('if').emitExpression(node.getChild('test'), forceBracket=True).append('\n')

        self.emitBlock(node.getChild('body'))

        elseBlock = node.getChild('orelse')

        if elseBlock and elseBlock.getChild('items'):
            elseItems = elseBlock.getChild('items')

            if len(elseItems) == 1 and elseItems[0].nodeType == NodeType.IF:
                self.emitIndent().append('else ')
                self.emitIf(elseItems[0], indent=False)
            else:
                self.emitIndent().append('else\n')
                self.emitBlock(elseBlock)

    def getForRangeInfo(self, node: Node) -> [Node, Node, Node, Node]:
        target = node.getChild('target')
        assert(target.nodeType == NodeType.NAME)
        index_var = Node.valueNode(target.getText())
        iter_ = node.getChild('iter')
        args = iter_.getChild('args')
        assert(1 <= len(args) <= 3)

        if len(args) == 1:
            start = Node.valueNode(0)
            end = args[0]
        else:
            start, end = args[:2]
        
        step = args[2] if len(args) == 3 else Node.valueNode(1)

        return index_var, start, end, step

    def emitForRangeConditionCheck(self, index_var, step, end) -> CResult:
        stepSign = get_sign(step)
        self.emitExpression(index_var)

        if stepSign == 1:
            self.append(' < ')
        elif stepSign == -1:
            self.append(' > ')
        else:
            self.append(f' * sign({step}) < ')

        self.emitExpression(end)

        if not stepSign:
            self.append(f' * sign({step})')

        return self

    def emitIfs(self, ifs: List[Node]):
        if ifs:
            self.emitIndent().append('if(!')
            if len(ifs) > 1: self.append('(')
            
            for i, if_ in enumerate(ifs):
                self.emitExpression(if_)
                if i+1 < len(ifs):
                    self.append(' && ')
            
            if len(ifs) > 1: self.append(')')
            self.append(') continue;\n')

    def emitForRange(self, node: Node, index: Node, emitBody):
        index_var, start, end, step = self.getForRangeInfo(node)
        
        self.emitIndent()
        self.append('for(int ').emitExpression(index_var).append(' = ').emitExpression(start).append('; ')
        self.emitForRangeConditionCheck(index_var, step, end).append('; ')
        self.emitExpression(index_var).append(' += ').emitExpression(step).append(')\n')

        self.emitIfs(node.getChild('ifs'))
            
        emitBody()

    def emitForRangeWithElse(self, node: Node):
        index_var, start, end, step = self.getForRangeInfo(node)
        stepSign = get_sign(step)

        self.emitIndent().append('{\n')                          # start block
        self.indent += 1
        
        self.emitIndent().append('int ').append(index_var).append(' = ').append(start).append(';\n')

        self.emitIndent().append('while(1)\n')                   # start while
        
        self.emitIndent().append('{\n')
        self.indent += 1

        self.emitIndent().append('if(').emitForRangeConditionCheck(index_var, step, end).append(')\n')

        self.emitBlock(node.getChild('body'))

        self.emitIndent().append('else\n')
                    
        self.emitIndent().append('{\n')                         # start else
        self.indent += 1

        self.emitBlock(node.getChild('orelse'))
        
        self.emitIndent().append('break;\n')
        self.indent -= 1

        self.emitIndent().append('}\n')                          # end else

        self.emitIndent().append(index_var).append(' += ').append(step).append(';\n')
        self.indent -= 1

        self.emitIndent().append('}\n')                          # end while        
        self.indent -= 1

        self.emitIndent().append('}\n')                          # end block

    def emitForListAssign(self, target: node, type_: Type, sub_indexes: List[int], iter_var: str, index_var: str):
        if target.nodeType in [NodeType.NAME, NodeType.VALUE]:
            self.emitIndent().append(type_.name)
            self.append(f' {target.getText()} = ')
            self.append(f'List__at({iter_var}, {index_var})')
            self.append(''.join([f'._{index}' for index in sub_indexes]))
            self.append(';\n')

        elif target.nodeType == NodeType.TUPLE:
            elts = target.getChild('elts')
            for i, elt in enumerate(elts):
                self.emitForListAssign(elt, type_.elementTypes[i], sub_indexes + [i], iter_var, index_var)
        else:
            raise Exception('Unknown node type:' + target.nodeType)
        
    def emitForList(self, node: Node, iter_: Node, index: Node, target: Node, emitBody):
        
        type_ = iter_.resolvedType
        iter_var = iter_.getText()
        index_var = index.getText()
        useTmp = False

        if iter_.resolvedType.genericType.name == BuiltInType.LIST:
            if not iter_var:
                self.emitIndent().append('{\n')
                self.indent += 1
                self.emitIndent().append(f'{type_.name} __tmp__ = ')                
                self.emitExpression(iter_).append(';\n')
                iter_var = '__tmp__'
                useTmp = True
        else:
            elementType = iter_.resolvedType.elementTypes[0]
            self.emitIndent()
            self.append(f'List__{elementType.name} __tmp__ = {iter_.resolvedType.genericType.name}__toList(')
            self.emitExpression(iter_).append(');\n')
            iter_var = '__tmp__'
            useTmp = True
            
        self.emitIndent().append(f'for(int {index_var} = 0; {index_var} < ')
        self.append(f'List__len({iter_var});')
        self.append(f'{index_var}++)\n')

        self.emitIndent().append('{\n')
        self.indent += 1

        self.emitForListAssign(target, type_.elementTypes[0], [], iter_var, index_var)

        self.emitIfs(node.getChild('ifs'))

        emitBody()

        self.indent -= 1
        self.emitIndent().append('}\n')

        if useTmp:
            self.indent -= 1
            self.emitIndent().append('}\n')

    def emitForListWithElse(self, node: Node, iter_: Node, index: Node, target: Node):
        
        type_ = iter_.resolvedType
        index_var = index.getText()
        iter_var = iter_.getText()
        useTmp = False

        self.emitIndent().append('{\n')                          # start block
        self.indent += 1

        if iter_.resolvedType.genericType.name == BuiltInType.LIST:
            if not iter_var:
                self.indent += 1
                self.emitIndent().append(f'{type_.name} __tmp__ = ')                
                self.emitExpression(iter_).append(';\n')
                iter_var = '__tmp__'
                useTmp = True
        else:
            elementType = iter_.resolvedType.elementTypes[0]
            self.append(f'List__{elementType.name} __tmp__ = {iter_.resolvedType.genericType.name}__toList(')
            self.emitExpression(iter_).append(');\n')
            iter_var = '__tmp__'
            useTmp = True

        self.emitIndent().append(f'int {index_var} = 0;\n')

        self.emitIndent().append('while(1)\n')                   # start while
        
        self.emitIndent().append('{\n')
        self.indent += 1

        self.emitIndent().append(f'if({index_var} < List__len({iter_var}))\n')
        
        self.emitIndent().append('{\n')
        self.indent += 1

        self.emitForListAssign(target, type_.elementTypes[0], [], iter_var, index_var)

        self.emitBlock(node.getChild('body'))
        self.indent -= 1

        self.emitIndent().append('}\n')

        self.emitIndent().append('else\n')
                    
        self.emitIndent().append('{\n')                         # start else
        self.indent += 1

        self.emitBlock(node.getChild('orelse'))
        
        self.emitIndent().append('break;\n')
        self.indent -= 1

        self.emitIndent().append('}\n')                          # end else

        self.emitIndent().append(f' {index_var} ++; \n')
        self.indent -= 1

        self.emitIndent().append('}\n')                          # end while        
        self.indent -= 1

        self.emitIndent().append('}\n')                          # end block

    def emitForZip(self, node: Node, iter_: Node, index: Node, targets: List[Node], emitBody):

        args = iter_.getChild('args')
        iter_vars = [arg.getText() for arg in args]
        index_var = index.getText()

        self.emitIndent().append('{\n')
        self.indent += 1

        for i, arg in enumerate(args):
            assert(arg.resolvedType.genericType != None)

            if arg.resolvedType.genericType.name == BuiltInType.LIST:
                if not arg.getText():
                    self.emitIndent()
                    self.append(f'{arg.resolvedType.name} __tmp__{i}__ = ')
                    self.emitExpression(arg).append(';\n')
                    iter_vars[i] = f'__tmp__{i}__'
            else:
                argElementType = arg.resolvedType.elementTypes[0]
                self.emitIndent()
                self.append(f'List__{argElementType.name} __tmp__{i}__ = {arg.resolvedType.genericType.name}__toList(')
                self.emitExpression(arg).append(');\n')
                iter_vars[i] = f'__tmp__{i}__'
        
        self.emitIndent().append(f'int __max__ = List__len({iter_vars[0]});\n')
        
        for iter_var in iter_vars[1:]:
            self.emitIndent().append(f'if(__max__ > List__len({iter_var})) __max__ = List_len({iter_var});\n')
            
        self.emitIndent().append(f'for(int {index_var} = 0; {index_var} < __max__; {index_var}++)\n')

        self.emitIndent().append('{\n')
        self.indent += 1
            
        if len(targets) == 1:
            target_var = targets[0].getText()
            typeName = targets[0].resolvedType.name
            
            for i, iter_var in enumerate(iter_vars):
                elementType = targets[0].resolvedType.elementTypes[i]
                tmp_target = Node.valueNode(f'__target__{i}__')
                self.emitForListAssign(tmp_target, elementType, [], iter_var, index_var)
            
            self.emitIndent()
            self.append(f'{typeName} {target_var} = ({typeName}) {{')
            self.append(', '.join([f'__target__{i}__' for i in range(len(iter_vars))]))
            self.append('};\n')
            
        else:
            assert(len(targets) == len(iter_vars))

            for i, iter_var in enumerate(iter_vars):
                elementType = targets[i].resolvedType
                self.emitForListAssign(targets[i], elementType, [], iter_var, index_var)
        
        self.emitIfs(node.getChild('ifs'))

        emitBody()

        self.indent -= 1
        self.emitIndent().append('}\n')

        self.indent -= 1
        self.emitIndent().append('}\n')

    def emitForZipWithElse(self, node: Node, iter_: Node, index: Node, targets: List[Node]):        
        args = iter_.getChild('args')
        iter_vars = [arg.getText() for arg in args]
        index_var = index.getText()

        self.emitIndent().append('{\n')                          # start block
        self.indent += 1

        for i, arg in enumerate(args):
            assert(arg.resolvedType.genericType != None)

            if arg.resolvedType.genericType.name == BuiltInType.LIST:
                if arg.nodeType not in [NodeType.NAME, NodeType.ATTR]:
                    self.emitIndent()
                    self.append(f'{arg.resolvedType.name} __tmp__{i}__ = ')
                    self.emitExpression(arg).append(';\n')
                    iter_vars[i] = f'__tmp__{i}__'
            else:
                argElementType = arg.resolvedType.elementTypes[0]
                self.emitIndent()
                self.append(f'List__{argElementType.name} __tmp__{i}__ = {arg.resolvedType.genericType.name}__toList(')
                self.emitExpression(arg).append(');\n')
                iter_vars[i] = f'__tmp__{i}__'
                
        self.emitIndent()
        self.append(f'int __max__ = List__len({iter_vars[0]});\n')
        
        for iter_var in iter_vars[1:]:
            self.emitIndent();
            self.append(f'if(__max__ > List__len({iter_var})) __max__ = List_len({iter_var});\n')

        self.emitIndent().append(f'int {index_var} = 0;\n')

        self.emitIndent().append('while(1)\n')                   # start while
        
        self.emitIndent().append('{\n')
        self.indent += 1

        self.emitIndent().append(f'if({index_var} < __max__)\n')
        
        self.emitIndent().append('{\n')
        self.indent += 1

        if len(targets) == 1:
            target_var = targets[0].getText()
            typeName = targets[0].resolvedType.name
            
            for i, iter_var in enumerate(iter_vars):
                elementType = targets[0].resolvedType.elementTypes[i]
                self.emitIndent()
                self.append(elementType.name).append(f' __target__{i}__ = ')
                self.append(f'List__at({iter_var}, {index_var});\n')
            
            self.emitIndent()
            self.append(f'{typeName} {target_var} = ({typeName}) {{')
            self.append(', '.join([f'__target__{i}__' for i in range(len(iter_vars))]))
            self.append('};\n')
            
        else:
            assert(len(targets) == len(iter_vars))

            for i, iter_var in enumerate(iter_vars):
                elementType = targets[i].resolvedType
                self.emitIndent()
                self.append(elementType.name).append(f' {targets[i].getText()} = ')
                self.append(f'List__at({iter_var}, {index_var});\n')

        self.emitBlock(node.getChild('body'))
        self.indent -= 1

        self.emitIndent().append('}\n')

        self.emitIndent().append('else\n')
                    
        self.emitIndent().append('{\n')                         # start else
        self.indent += 1

        self.emitBlock(node.getChild('orelse'))
        
        self.emitIndent().append('break;\n')
        self.indent -= 1

        self.emitIndent().append('}\n')                          # end else

        self.emitIndent().append(f' {index_var} ++; \n')
        self.indent -= 1

        self.emitIndent().append('}\n')                          # end while        
        self.indent -= 1

        self.emitIndent().append('}\n')                          # end block

    def emitForSetAssign(self, target: node, type_: Type, sub_indexes: List[int]):
        if target.nodeType in [NodeType.NAME, NodeType.VALUE]:
            self.emitIndent().append(type_.name)
            self.append(f' {target.getText()} = ')
            self.append(f'__next__->key')
            self.append(''.join([f'._{index}' for index in sub_indexes]))
            self.append(';\n')

        elif target.nodeType == NodeType.TUPLE:
            elts = target.getChild('elts')
            for i, elt in enumerate(elts):
                self.emitForSetAssign(elt, type_.elementTypes[i], sub_indexes + [i])
        else:
            raise Exception('Unknown node type:' + target.nodeType)

    def emitForSet(self, node: Node, iter_: Node, target: Node, emitBody):        
        type_ = iter_.resolvedType
        iter_var = iter_.getText()
        useTmp = not iter_var

        self.emitIndent().append('{\n')                         # start block
        self.indent += 1

        if useTmp:
            self.emitIndent()
            self.append(f'{type_.name} __tmp__ = ').emitExpression(iter_).append(';\n')
            iter_var = '__tmp__'
       
        self.emitIndent().append(f'{type_.name}__iter __next__')
        self.append(f' = Set__head({iter_var});\n')

        self.emitIndent().append('while(1)\n')
        
        self.emitIndent().append('{\n')                         # start while
        self.indent += 1

        self.emitIndent().append('if(__next__)\n')
        
        self.emitIndent().append('{\n')
        self.indent += 1

        self.emitForSetAssign(target, type_.elementTypes[0], [])

        self.emitIfs(node.getChild('ifs'))

        emitBody()

        self.indent -= 1
        self.emitIndent().append('}\n')

        self.emitIndent().append('else\n')
                    
        self.emitIndent().append('{\n')                          # start else
        self.indent += 1

        elseBlock = node.getChild('orelse')
        if elseBlock and elseBlock.getChild('items'):
            self.emitBlock(elseBlock)
        
        self.emitIndent().append('break;\n')
        self.indent -= 1

        self.emitIndent().append('}\n')                          # end else

        self.emitIndent().append('__next__ = Set__next(__next__);\n')           
        self.indent -= 1

        self.emitIndent().append('}\n')                          # end while
        self.indent -= 1

        self.emitIndent().append('}\n')                          # end block

    def emitForDictAssign(self, target: node, type_: Type, target_attr: str, sub_indexes: List[int]):
        if target.nodeType in [NodeType.NAME, NodeType.VALUE]:
            self.emitIndent().append(type_.name)
            self.append(f' {target.getText()} = ')
            self.append(f'__next__->{target_attr}')
            self.append(''.join([f'._{index}' for index in sub_indexes]))
            self.append(';\n')

        elif target.nodeType == NodeType.TUPLE:
            elts = target.getChild('elts')
            for i, elt in enumerate(elts):
                self.emitForDictAssign(elt, type_.elementTypes[i], target_attr, sub_indexes + [i])
        else:
            raise Exception('Unknown node type:' + target.nodeType)

    def emitForDict(self, node: Node, iter_: Node, targets: List[Node], target_attrs: List[str], emitBody):
        type_ = iter_.resolvedType
        iter_var = iter_.getText()
        useTmp = not iter_var

        self.emitIndent().append('{\n')                      # start block
        self.indent += 1

        if useTmp:
            self.emitIndent()
            self.append(f'{type_.name} __tmp__ = ').emitExpression(iter_).append(';\n')
            iter_var = '__tmp__'
        
        self.emitIndent().append(f'{type_.name}__iter __next__')
        self.append(f' = Dict__head({iter_var});\n')

        self.emitIndent().append('while(1)\n')
        
        self.emitIndent().append('{\n')                      # start while
        self.indent += 1

        self.emitIndent().append('if(__next__)\n')
        
        self.emitIndent().append('{\n')
        self.indent += 1

        for i, target in enumerate(targets):
            self.emitForDictAssign(target, target.resolvedType, target_attrs[i], [])

        self.emitIfs(node.getChild('ifs'))

        emitBody()

        self.indent -= 1
        self.emitIndent().append('}\n')

        self.emitIndent().append('else\n')
                    
        self.emitIndent().append('{\n')                          # start else
        self.indent += 1

        elseBlock = node.getChild('orelse')
        if elseBlock and elseBlock.getChild('items'):
            self.emitBlock(elseBlock)
        
        self.emitIndent().append('break;\n')
        self.indent -= 1

        self.emitIndent().append('}\n')                          # end else

        self.emitIndent().append('__next__ = Dict__next(__next__);\n')           
        self.indent -= 1

        self.emitIndent().append('}\n')                          # end while
        self.indent -= 1

        self.emitIndent().append('}\n')                          # end block

    def emitFor(self, node: Node, emitBody=None):
        iter_ = node.getChild('iter')
        type_ = iter_.resolvedType
        elseBlock = node.getChild('orelse')
        hasElse = elseBlock and elseBlock.getChild('items')
        
        isList, isDict = False, False
        index = Node.valueNode('__index__')
        target = node.getChild('target')
        assert(target.nodeType in [NodeType.NAME, NodeType.TUPLE])
        
        if type_.genericType and type_.genericType.name == BuiltInType.ENUMERATE:                
            args = iter_.getChild('args')
            elts = target.getChild('elts')

            assert(len(args) == 1)
            assert(target.nodeType == BuiltInType.TUPLE)               
            assert(len(elts) == 2)

            index = elts[0]
            target = elts[1]
            iter_ = args[0]
            type_ = iter_.resolvedType
            assert(type_.name != BuiltInType.RANGE)
            if type_.genericType.name != BuiltInType.ZIP:
                isList = True
            
        genericType = type_.genericType
        genericTypeName = genericType.name if genericType else ''

        if genericTypeName == BuiltInType.LIST:
            isList = True

        if genericTypeName == BuiltInType.DICT:
            isDict = True

        if target.nodeType == NodeType.NAME:
            targets = [target]
        else:
            targets = target.getChild('elts')

        if iter_.nodeType == NodeType.CALL:
            func = iter_.getChild('func')

            if func.nodeType == NodeType.ATTR:
                value = func.getChild('value')
                type_ = value.resolvedType
                genericType = type_.genericType
                if genericType and genericType.name == BuiltInType.DICT:                    
                    attr = func.getChild('attr')
                    assert(attr in ['keys', 'values', 'items'])
                    
                    isDict = True
                    isList = False
                    iter_ = value
                    target_attr = {'keys' : 'item->key', 'values': 'item->value', 'items': 'item'}[attr]
                    
                    if len(targets) == 1:
                        target_attrs = [target_attr]
                    else:
                        assert(attr == 'items' and len(targets) == 2)
                        target_attrs = ['item->key', 'item->value']

        elif genericTypeName == BuiltInType.DICT:
            assert(len(targets) == 1)
            target_attrs = ['item->key']
            
        emitBlock = lambda: self.emitBlock(node.getChild('body'))

        if type_.name == BuiltInType.RANGE:
            if hasElse:
                self.emitForRangeWithElse(node)
            else:
                self.emitForRange(node, emitBody=emitBody or emitBlock)

        elif isList:
            if hasElse:
                self.emitForListWithElse(node, iter_=iter_, index=index, target=target)
            else:
                self.emitForList(node, iter_=iter_, index=index, target=target, emitBody=emitBody or emitBlock)

        elif genericTypeName == BuiltInType.SET:
            self.emitForSet(node, iter_=iter_, target=target, emitBody=emitBody or emitBlock)

        elif isDict :
            self.emitForDict(node, iter_=iter_, targets=targets, target_attrs=target_attrs, emitBody=emitBody or emitBlock)
        
        elif genericTypeName == BuiltInType.ZIP:
            if hasElse:
                self.emitForZipWithElse(node, iter_=iter_, index=index, targets=targets)
            else:
                self.emitForZip(node, iter_=iter_, index=index, targets=targets, emitBody=emitBody or emitBlock)
        else:
            raise Exception('Cannot iter over ' + type_.name)

    def emitWhile(self, node):
        elseBlock = node.getChild('orelse')
        
        if not elseBlock or not elseBlock.getChild('items'):
            self.emitIndent().append('while')
            self.emitExpression(node.getChild('test'), forceBracket=True).append('\n')
            self.emitBlock(node.getChild('body'))
        else:
            self.emitIndent()
            self.append('while(1)\n')
            
            self.emitIndent().append('{\n')
            self.indent += 1

            self.emitIndent().append('if')
            self.emitExpression(node.getChild('test'), forceBracket=True).append('\n')

            self.emitBlock(node.getChild('body'))

            self.emitIndent().append('else\n')

            self.emitIndent().append('{\n')
            self.indent += 1

            self.emitBlock(elseBlock)
            
            self.emitIndent().append('break;\n')
        
            self.indent -= 1
            self.emitIndent().append('}\n')

            self.indent -= 1
            self.emitIndent().append('}\n')

    def emitBlock(self, node, bracket=True):
        items = node.getChild('items')
        self.emitIndent()

        if not items:
            self.append("{}\n" if bracket else '')
            return

        scope = node.scope
        if bracket:
            self.append("{\n")
            self.indent += 1
        
        for variable in scope.variables:
            self.emitVariable(variable)

        for item in items:
            if item.nodeType == NodeType.BLOCK:
                self.emitBlock(item)

            elif item.nodeType == NodeType.EXPR:
                self.emitIndent()
                self.emitExpression(item.getChild('value')).append(';\n')

            elif item.nodeType == NodeType.CLASS:
                self.emitClass(item)

            elif item.nodeType == NodeType.FUNCTION:
                self.emitFunction(item)

            elif item.nodeType == NodeType.IF:
                self.emitIf(item)

            elif item.nodeType == NodeType.FOR:
                self.emitFor(item)

            elif item.nodeType == NodeType.WHILE:
                self.emitWhile(item)
            
            elif item.nodeType == NodeType.CONTINUE:
                self.emitIndent().append('continue;\n')

            elif item.nodeType == NodeType.BREAK:
                self.emitIndent().append('break;\n')

            elif item.nodeType in [NodeType.ASSIGN, NodeType.ANN_ASSIGN]:
                if item.nodeType == NodeType.ASSIGN:
                    targets = item.getChild('targets')
                else:
                    targets = [item.getChild('target')]

                value = item.getChild('value')

                for target in targets:
                    self.emitAssign(target, value)

            elif item.nodeType == NodeType.AUG_ASSIGN:
                self.emitAugAssign(item)
            
            elif item.nodeType == NodeType.RETURN:
                self.emitReturn(item)

        if bracket:
            self.indent -= 1
            self.emitIndent().append('}\n')

    def emitImplement(self, node: Node):
        self.emitBlock(node.getChild('body'), False)

    def emitClassDef(self, node: Node):
        className = node.getChild('name')
        self.append('typedef struct \n{\n')
        self.indent += 1

        for field in node.scope.class_fields:
            self.emitIndent()
            self.append(field.type_.name)
            self.append(' ').append(field.name).append(';\n')
        
        self.indent -= 1
        self.append(f'}} __{className}__body__, *{className};\n\n')
    
    def emitTupleDef(self, type_: Type):
        elementTypes = type_.elementTypes
        self.append('typedef struct \n{\n')
        self.indent += 1

        for i, elementType in enumerate(elementTypes):
            self.emitIndent()
            self.append(elementType.name).append(f' _{i};\n')

        self.indent -= 1
        self.append(f'}} {type_.name} ;\n\n')


    def emitDefinition(self, node: Node):
        self.append('#include <stdlib.h>\n')
        self.append('#include <string.h>\n')
        self.append('#include "types.h"\n')
        self.append('\n')

        items = node.getChild('body').getChild('items')
        for item in items:
            if item.nodeType == NodeType.CLASS:
                self.emitClassDef(item)

        global_ = node.parentScope
        while global_.parent != None:
            global_ = global_.parent

        for symbol in global_.symbols:
            if not symbol.name.startswith(BuiltInType.TUPLE + '__'):
                continue

            if not symbol.resolvedType.genericType:
                continue
                
            if symbol.resolvedType.genericType.name == BuiltInType.TUPLE:
                self.emitTupleDef(symbol.resolvedType)

        self.append('\n')