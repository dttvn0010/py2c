class Foo:
    def __init__(self, x: int):
        self.x = x

class Bar:
    def __init__(self, foo: Foo):
        self.foo = foo

    def setFoo(self, foo: Foo):
        self.foo = foo

    def getFoo(self) -> Foo:
        return Foo(self.foo.x) #self.foo

class Baz:
    def __init__(self, bar: Bar):
        self.bar = bar

def copyFoo(bar: Bar, foo: Foo):
    bar.foo = foo

def copyBarFoo(bar1: Bar, bar2: Bar):
    bar1.foo = bar2.foo

def testInit(baz: Baz, bar: Bar):
    baz.bar = bar

def main() -> int:
    foo = Foo(10)
    bar = Bar(foo)
    baz = Baz(bar)
    if True:
        foo2 = Foo(20)
        bar2 = Bar(foo2)
        #copyFoo(bar, foo)
        #testInit(baz, Bar(foo))
        copyBarFoo(bar, bar2)
    return 0