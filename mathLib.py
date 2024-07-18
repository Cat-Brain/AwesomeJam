class Vec2:
    x: int
    y: int
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
    
    def __str__(self):
        return f"({self.x}, {self.y})"
    

class Vec2f:
    x: float
    y: float
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
    
    def __str__(self):
        return f"({self.x}, {self.y})"