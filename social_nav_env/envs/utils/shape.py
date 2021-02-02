from abc import ABC, abstractmethod

class Shape(ABC):
    def __init__(self, pos, color=None):
        self.x = pos[0]
        self.y = pos[1]
    
    @abstractmethod
    def to_poly(self):
        pass

class CornerRect(Shape):
    def __init__(self, pos, width, height):
        super().__init__(pos)
        self.width = width
        self.height = height
    
    def to_poly(self):
        point1 = (self.x, self.y)
        point2 = (self.x + self.width, self.y)
        point3 = (self.x + self.width, self.y + self.height)
        point4 = (self.x, self.y + self.height)
        return [point1,point2,point3,point4]

class CentreRect(Shape):
    def __init__(self, pos, width, height):
        super().__init__(pos)
        self.width = width
        self.height = height
    
    def to_poly(self):
        point1 = (self.x - self.width/2, self.y - self.height/2)
        point2 = (self.x + self.width/2, self.y - self.height/2)
        point3 = (self.x + self.width/2, self.y + self.height/2)
        point4 = (self.x - self.width/2, self.y + self.height/2)
        return [point1,point2,point3,point4]