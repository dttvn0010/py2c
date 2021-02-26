from __future__ import annotations
from symbol import Symbol
from typing import List
from type_ import Type

class Scope:
    def __init__(self, parent: Scope=None):        
        self.parent = parent
        self.symbols: List[Symbol] = []
        self.classType: Type = None
        self.children : List[Scope] = []
        self.hasGoToEnd = False
        self.hasReturn = False
        self.hasForQuit = False     # break/continue
        self.isFunction = False
        self.isLoop = False
        if parent != None:
            self.name =  parent.name + '_' + str(len(parent.children))
            self.depth = parent.depth + 1
            parent.children.append(self)
        else:
            self.name = 'Scope'
            self.depth = 0
    
    def findLocal(self, name:str):
        return next((x for x in self.symbols if x.name == name), None)
        
    def findNested(self, name: str)-> Symbol:
        scope = self
        while scope != None:
            local = scope.findLocal(name)
            if local != None:
                return local
            
            scope = scope.parent

    def define(self, symbol: Symbol) -> bool:
        existing = self.findLocal(symbol.name)
        if existing != None:
            print(symbol.range_, 'Duplicate symbol:', symbol.name)
            return False
                
        self.symbols.append(symbol)
        symbol.scope = self
        symbol.minScopeDepth = self.depth
        
        return True
       
    def getVariables(self) -> List[Symbol]:
        return [sym for sym in self.symbols if sym.isVariable()]

    def hasReferenceVariable(self):
        for var in self.getVariables():
            if var.resolvedType.isClass():
                return True

        return False
