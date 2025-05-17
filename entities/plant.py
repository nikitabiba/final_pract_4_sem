from entities.base_entity import Entity
from logger import setup_logger
from meta_classes import EvalPlantMeta

logger = setup_logger(__name__)

class Plant(Entity, metaclass=EvalPlantMeta):
    def __init__(self, x, y, symbol, world, timer, is_growing=0, active=0):
        super().__init__(x, y, symbol, world, timer)
        self.is_growing = is_growing
        self.active = active
        logger.debug(f"Plant created at ({x}, {y})")