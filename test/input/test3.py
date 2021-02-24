def print(s: int):
    pass

class Point:
    def __init__(self, x:int, y:int):
        self.x = x
        self.y = y

def testFor1(N: int) -> int:
    s = 0
    for i in range(N):
        s += i

    for i in range(N):
        s += i
        if i > 100:
            tmp = Point(0, 0)
            if i > 200:
                tmp2 = Point(1, 2)
                if i > 300:
                    break
        print(s)
    else:
        s += N
    return s

def testFor2(lst: List[int]) -> int:
    s = 0
    for i in lst:
        s += i        

    for i in lst:
        s += i
        if i > 100:
            continue
        print(s)
    else:
        s *= 2

    return s


def square(lst: List[float]) -> List[float]:
    return [x*x for x in lst]

def test1() -> (int, int):
    i, j = 1, 2
    x = y, z = i, j
    return i, y

def test2(x: Set[int], y: List[int]):
    lst = [index + i + j for index,(i,j) in enumerate(zip(x,y))]

def test3(lst: List[Tuple[int, int]]):
    for i, j in lst:
        print(i, j)

def test4(y: List[int], d: Dict[int, int]):
    t :int = 1
    z : List[int] = [1, 2, 3, 4]
    s = {1, 2, 3, 4, 5}
    d2 = d
    d2 = {1:2, 3: 4, 5: 10}
    z[1] = y.get(t, 0)
    d2[2] = 3      