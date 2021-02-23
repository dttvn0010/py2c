from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from node import Node
    from scope import Scope
      
class Symbol:    
    def __init__(self, name: str, resolvedType=None, isClass=False):
        self.name = name
        self.resolvedType = resolvedType
        self.isClass = isClass
        
    def __repr__(self):
        return self.name