class Point:
    def __init__(self, x: float32, y: float32):
        self.x = x
        self.y = y

    def getX(self) -> float32:
        return self.x

    def getY(self) -> float32:
        return self.y

    def add(self, pt: Point) -> Point:
        return Point(self.getX() + pt.x, self.y + pt.getY())

class Line:
    def __init__(self, pt1: Point, pt2: Point):
        self.pt1 = pt1
        self.pt2 = pt2

    def getMidPoint(self) -> Point:
        return Point(
                (self.pt1.x + self.pt2.x)/2, 
                (self.pt1.y + self.pt2.y)/2
        )

    def setPoint1(self, x1: float, y1: float):
        self.pt1 = Point(x1, y1)

    def setPoint2(self, pt: Point):
        self.pt2 = pt

def newLine(x1: float32, y1: float32, x2: float32, y2: float32) -> Line:
    pt1 = Point(x1, y1)
    pt2 = Point(x2, y2)
    line = Line(pt1, pt2)
    return line

def newPoint(x: float32, y: float32) -> Point:
    if x > 0:
        tmp0 = Point(0.0, 0.0)
        if y > 0:
            tmp1 = Point(x, y)
            return tmp1
        else:
            tmp2 = Point(x, -y)
            if x > 1:
                return tmp2
            x = 1
    else:        
        tmp3 = Point(-x, y)
        return tmp3

def print(x: float32, y: float32):
    pass

def testPoint(pt: Point):
    print(pt.x, pt.y)

def test() -> Line:
    line = newLine(0.0, 1.0, 1.0, 0.0)
    line.setPoint1(1.0, 2.0)
    

    testPoint(line.pt1)
    testPoint(line.pt2)

    pt = Point(0.0, 0.0)
    testPoint(pt)

    testPoint(Point(1.0, 1.0))

    testPoint(newPoint(0.0, 1.0))

    line.setPoint2(pt)

    return line
    
    