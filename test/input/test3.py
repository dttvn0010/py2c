def sum(lst: List[int]) -> int:
    s = 0
    for i in lst:
        s += i
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