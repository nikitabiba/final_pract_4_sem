from entities.base_entity import Entity
import random
import copy
from logger import setup_logger
from meta_classes import EvalAnimalMeta

logger = setup_logger(__name__)

class Animal(Entity, metaclass=EvalAnimalMeta):
    def __init__(self, x, y, symbol, world, timer, group, eatable_entities, reproduce_condition, eat_condition, hunger=100):
        super().__init__(x, y, symbol, world, timer)
        self.hunger = hunger
        self.group = group
        self.eatable_entities = eatable_entities
        self.reproduce_condition = reproduce_condition
        self.eat_condition = eat_condition
        logger.debug(f"Animal {self.symbol} at ({self.x}, {self.y}) has arrived.")