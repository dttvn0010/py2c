class Point:
    def __init__(self, x: float32, y: float32):
        self.x : float64 = x
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