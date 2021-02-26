from __future__ import annotations
from typing import TYPE_CHECKING
from enum import Enum

if TYPE_CHECKING:
    from node import Node
    from scope import Scope
      
class SymbolKind(Enum):
    CLASS = 1
    FUNCTION = 2
    VARIABLE = 3
    
class Symbol:    
    def __init__(self, name: str, resolvedType=None, symbolKind=SymbolKind.VARIABLE):
        self.name = name
        self.resolvedType = resolvedType
        self.symbolKind = symbolKind
        self.initialized = False
        self.scope: Scope = None
        self.minScopeDepth = -1

    def isVariable(self):
        return self.symbolKind == SymbolKind.VARIABLE

    def isFunction(self):
        return self.symbolKind == SymbolKind.FUNCTION

    def isClass(self):
        return self.symbolKind == SymbolKind.CLASS
        
    def __repr__(self):
        return self.name