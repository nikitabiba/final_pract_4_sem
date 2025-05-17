import random
import copy
from logger import setup_logger

logger = setup_logger(__name__)

class Grid:
    def __init__(self, width, height, cells):
        self.width = width
        self.height = height
        self.cells = cells

    def is_in_bounds(self, x, y):
        if x is not None or y is not None:
            return (0 <= x and x < self.width) and (0 <= y and y < self.height)
    
    def place_entity(self, entity, x, y):
        if self.is_in_bounds(x, y) and self.cells[y][x] is None:
            self.cells[y][x] = entity
            entity.x = x
            entity.y = y
            entity.world = self

    def move_entity(self, entity, new_x, new_y):
        if self.is_in_bounds(new_x, new_y):
            self.cells[entity.y][entity.x] = None
            self.cells[new_y][new_x] = entity
            entity.x = new_x
            entity.y = new_y

    def duplicate_entity(self, entity, new_x, new_y):
        if self.is_in_bounds(new_x, new_y):
            new_entity = copy.deepcopy(entity)
            self.cells[new_y][new_x] = new_entity
            new_entity.x = new_x
            new_entity.y = new_y
            new_entity.world = self

    def remove_entity(self, entity):
        if entity.x is not None and entity.y is not None:
            self.cells[entity.y][entity.x] = None
            entity.world = None
            entity.x = None
            entity.y = None

    def get_neighbors(self, x, y):
        neighbors = []
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if self.is_in_bounds(nx, ny):
                neighbors.append([self.cells[ny][nx], nx, ny])
        return neighbors
    
    def tick(self):
        entities = [cell for row in self.cells for cell in row if cell is not None]
        random.shuffle(entities)

        for entity in entities:
            entity.act()
