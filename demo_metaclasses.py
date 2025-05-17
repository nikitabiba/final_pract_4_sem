import random
from world.grid import Grid
from world.time_manager import TimeManager
from entity_factory import create_plant_class, create_animal_class
from entities.group import Group
from entities.plants.lumiere import Lumiere
from entities.plants.obscurite import Obscurite
from entities.plants.demi import Demi
from meta_classes import entity_registry
from logger import setup_logger

logger = setup_logger("demo")

def create_empty_grid(width, height):
    return [[None for _ in range(width)] for _ in range(height)]


def demo_dynamic_classes():
    """
    Демонстрирует динамическое создание классов с использованием метаклассов
    """
    logger.info("=== DEMONSTRATION OF DYNAMIC CLASS CREATION ===")
    
    # Создаем новый класс растения
    NightFlower = create_plant_class(
        name="NightFlower",
        symbol="N",
        active_phases=['night'],
        inactive_phases=['day'],
        semi_active_phases=['evening']
    )
    
    # Отображаем информацию о новых классах из реестра
    logger.info("New classes registered in the entity registry:")
    if 'NightFlower' in entity_registry['plants']:
        plant_class = entity_registry['plants']['NightFlower']
        logger.info(f"Plant class: {plant_class.__name__}")
        logger.info(f"  - Active phases: {plant_class.ACTIVE_PHASES}")
        logger.info(f"  - Inactive phases: {plant_class.INACTIVE_PHASES}")
        logger.info(f"  - Semi-active phases: {plant_class.SEMI_ACTIVE_PHASES}")
    
    # Создаем мини-экосистему с новыми классами
    logger.info("\nTesting mini-ecosystem with new classes...")
    grid = Grid(50, 50, create_empty_grid(50, 50))
    timer = TimeManager(5)
    
    # Создаем группу для нового животного
    hunter_group = Group(99)
    
    for i in range(3):
        x, y = random.randint(0, 49), random.randint(0, 49)
        if grid.cells[y][x] is None:
            night_flower = NightFlower(x, y, "N", world=grid, timer=timer)
            grid.place_entity(night_flower, x, y)
            logger.info(f"Placed NightFlower at ({x}, {y})")
    
    for i in range(3):
        x, y = random.randint(0, 49), random.randint(0, 49)
        if grid.cells[y][x] is None:
            lumiere = Lumiere(x, y, "L", grid, timer)
            grid.place_entity(lumiere, x, y)
            logger.info(f"Placed Lumiere at ({x}, {y})")
    
    # Симуляция нескольких тиков
    logger.info("\nRunning mini-simulation...")
    for tick in range(10):
        logger.info(f"\n--- Tick {tick+1} | Time phase: {timer.current_phase} ---")
        grid.tick()
        timer.advance_time()
    
    logger.info("Dynamic class demo completed.")


def demo_method_injection():
    """
    Демонстрирует инжекцию методов в классы через метаклассы
    """
    logger.info("\n=== DEMONSTRATION OF METHOD INJECTION ===")
    
    grid = Grid(5, 5, create_empty_grid(5, 5))
    timer = TimeManager(5)
    
    lumiere = Lumiere(1, 1, "L", grid, timer)
    obscurite = Obscurite(2, 2, "O", grid, timer)
    demi = Demi(3, 3, "D", grid, timer)
    
    grid.place_entity(lumiere, 1, 1)
    grid.place_entity(obscurite, 2, 2)
    grid.place_entity(demi, 3, 3)
    
    phases = ['morning', 'day', 'evening', 'night']
    
    for phase in phases:
        logger.info(f"\nTesting plant behavior in phase: {phase}")
        timer.current_phase = phase
        
        logger.info("Lumiere behavior:")
        lumiere.grow()
        logger.info(f"  - Is growing: {lumiere.is_growing}")
        logger.info(f"  - Activity level: {lumiere.active}")
        
        logger.info("Obscurite behavior:")
        obscurite.grow()
        logger.info(f"  - Is growing: {obscurite.is_growing}")
        logger.info(f"  - Activity level: {obscurite.active}")
        
        logger.info("Demi behavior:")
        demi.grow()
        logger.info(f"  - Is growing: {demi.is_growing}")
        logger.info(f"  - Activity level: {demi.active}")
    
    logger.info("Method injection demo completed.")


if __name__ == "__main__":
    demo_dynamic_classes()
    demo_method_injection()