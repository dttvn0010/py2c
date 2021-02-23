def max1(x: float, y: float) -> float:
    return x if x > y else y

def max2(x: float, y: float) -> float:
    if x > y:
        return x
    else:
        return y

def max3(x: float, y: float, z: float) -> float:
    if y <= x >= z:
        return x
    elif x <= y >= z:
        return y
    else:
        return z