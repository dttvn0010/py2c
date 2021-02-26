import ast
from typing import List
from node import Node, toNode
    
def parse(src: str) -> Node:
    return toNode(None, ast.parse(src))
    
def dump(node, include_attributes=False, *, indent=2):
    def _format(node, level=0):
        level += 1
        prefix = '\n' + indent * level
        sep = ',\n' + indent * level

        if isinstance(node, ast.AST):
            cls = type(node)
            args = []
            allsimple = True
            fields = list(node._fields)
            if include_attributes and node._attributes:
                fields += list(node._attributes)
                
            for name in fields:
                try:
                    value = getattr(node, name)
                except AttributeError:
                    continue
                if value is None and getattr(cls, name, ...) is None:
                    continue
                value, simple = _format(value, level)
                allsimple = allsimple and simple
                args.append(f'{name}={value}')
                
            if allsimple and len(args) <= 3:
                return f"{node.__class__.__name__}({', '.join(args)})", not args
                
            return f'{node.__class__.__name__}({prefix}{sep.join(args)})', False
            
        elif isinstance(node, list):
            if not node:
                return '[]', True
                
            return f'[{prefix}{sep.join(_format(x, level)[0] for x in node)}]', False
            
        return repr(node), True

    indent = ' ' * indent
    return _format(node)[0]
        
src = '''
def add(x: int, y: int) -> int:
    s = d = 0.0
    s1 = s
    s += x
    s = s / y
    test(x, y)
    if x > 1:
        if y > 1:
            t = x + y
            return t
    return s
'''        

ast_node = ast.parse(src)
#print(dump(ast_node, include_attributes=False, indent=2))

node = parse('''
def add(x: int, y: int) -> int:
    s = 1
    t = 2
    return x + y

def test(x: int, y:int):
    add(x, y)    
''')
print(node)