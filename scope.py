from __future__ import annotations
from symbol import Symbol
from variable import Variable
from typing import List

class Scope:
    def __init__(self):
        self.parent: Scope = None
        self.symbols: List[Symbol] = []
        self.variables : List[Variable] = []
        self.class_fields: List[Variable] = []
        self.className = ''
        
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
        
        return True
       
    def addVariable(self, var_name: str, var_type: str):
        self.variables.append(Variable(var_name, var_type))

    def addClassField(self, var_name: str, var_type: str):
        self.class_fields.append(Variable(var_name, var_type))