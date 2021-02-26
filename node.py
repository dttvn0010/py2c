from __future__ import annotations
from typing import TYPE_CHECKING, List
from symbol import Symbol
import ast

if TYPE_CHECKING:
    from scope import Scope
    from symbol import Symbol

class NodeType:
    GLOBAL = 'Global'
    MODULE = 'Module'
    CLASS = 'ClassDef'
    FUNCTION = 'FunctionDef'
    ARGUMENTS = 'arguments'
    ARG = 'arg'
    IF = 'If'
    IF_EXP = 'IfExp'
    FOR = 'For'
    WHILE = 'While'
    CONTINUE = 'Continue'
    BREAK = 'Break'
    EXPR = 'Expr'
    CALL = 'Call'
    ATTR = 'Attribute'
    BLOCK = 'Block'
    NAME = 'Name'
    SUBSCRIPT = 'Subscript'
    TUPLE = 'Tuple'
    LIST = 'List'
    SET = 'Set'
    DICT = 'Dict'
    RETURN = 'Return'
    NUM = 'Num'
    CONSTANT = 'Constant'
    ASSIGN = 'Assign'
    ANN_ASSIGN = 'AnnAssign'
    AUG_ASSIGN = 'AugAssign'
    UNARY_OP = 'UnaryOp'
    BIN_OP = 'BinOp'
    BOOL_OP = 'BoolOp'
    COMPARE = 'Compare'
    VALUE = 'value'
    LIST_COMP = 'ListComp'
    GEN_EXP = 'GeneratorExp'
    COMP = 'comprehension'
    
class Node:
    def __init__(self, parent: Node, nodeType: str, value=None):
        self.nodeType = nodeType
        self.value = value
        self.parent = parent
        self.children: List[Node] = {}
        self.scope: Scope = None
        self.parentScope: Scope = None
        self.range_ = ''
        self.internalRange = ''
        self.symbol : Symbol = None
        self.resolvedType : Type = None        
        
    def __getattr__(self, key):
        return self.children.get(key)
        
    def valueNode(value) -> Node:
        return Node(None, NodeType.VALUE, value)

    def isValue(self) -> bool:
        return self.nodeType == NodeType.VALUE
    
    def getText(self) -> str:
        if self.nodeType == NodeType.VALUE:
            return str(self.value)

        if self.nodeType == NodeType.NUM:
            return str(self.getChild('n'))

        if self.nodeType == NodeType.CONSTANT:
            return str(self.getChild('value'))

        if self.nodeType == NodeType.NAME:
            return str(self.getChild('id'))
        
        if self.nodeType == NodeType.ATTR:
            return self.getChild('value').getText() + '.__body__->' + self.getChild('attr')

    def isExpression(self) -> bool:
        return self.nodeType in [
            NodeType.NAME, 
            NodeType.NUM, 
            NodeType.CONSTANT, 
            NodeType.IF_EXP, 
            NodeType.BIN_OP, 
            NodeType.UNARY_OP, 
            NodeType.BOOL_OP, 
            NodeType.COMPARE, 
            NodeType.VALUE, 
            NodeType.ATTR,
            NodeType.CALL,
            NodeType.LIST,
            NodeType.TUPLE,
            NodeType.SET,
            NodeType.DICT,
            NodeType.SUBSCRIPT,
            NodeType.LIST_COMP,
            NodeType.GEN_EXP
        ]
        
    def getChild(self, field) -> Node:
        if field in self.children:
            child_node = self.children[field]
            if not isinstance(child_node, list) and child_node.isValue():
                return child_node.value
            return child_node

    def getChildNodes(self) -> List[Node]:
        child_nodes = []

        for child_node in self.children.values():
            if isinstance(child_node, list):
                child_nodes += child_node            
            elif not child_node.isValue():
                child_nodes.append(child_node)

        return child_nodes
                
    def to_str(self, level=0):
        tab = "  "
        indent = tab * level
        if self.nodeType == 'value':
            return indent + str(self.value)
            
        st = indent + self.nodeType
        
        if self.children:
            st += '(\n'
            for key, value in self.children.items():                
                st += indent + tab  + f'{key}='
                if isinstance(value, list):
                    if not value:
                        st += '[]\n'
                    else:
                        st += '[\n'
                        for x in value:
                            st += f'{x.to_str(level+2)}\n'
                        st += indent + tab + '],\n'
                else:
                    st += f'{value.to_str(level+1)}'.strip() + ',\n'
                    
            st += indent + ')'
        else:
            st += '()'
            
        return st
            
    def __repr__(self):
        return self.to_str()
        
        return st
        
def toNode(parent, ast_node) -> Node:
    if isinstance(ast_node, list):
        return [toNode(parent, x) for x in ast_node]
        
    if not isinstance(ast_node, ast.AST):
        return Node(parent, 'value', ast_node)
        
    node = Node(parent, ast_node.__class__.__name__)
    fields = list(ast_node._fields)
    if ast_node._attributes:
        fields += list(ast_node._attributes)
        
    cls = type(ast_node)
    node.children = {}
    
    for name in fields:
        try:
            value = getattr(ast_node, name)
        except AttributeError:
            continue
        if value is None and getattr(cls, name, ...) is None:
            continue
            
        child_node = toNode(node, value)

        if name in ['body', 'orelse']:
            bodyNode = Node(node, 'Block')
            bodyNode.children['items'] = child_node
            node.children[name] = bodyNode
        else:
            node.children[name] = child_node
        
    return node
    