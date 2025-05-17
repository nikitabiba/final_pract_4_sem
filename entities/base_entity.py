class Entity:
    def __init__(self, x, y, symbol, world, timer):
        self.x = x
        self.y = y
        self.symbol = symbol
        self.world = world
        self.timer = timer

    def act(self):
        pass
