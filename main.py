import random
from world.grid import Grid
from world.time_manager import TimeManager
from entities.animals.malheureux import Malheureux
from entities.animals.pauvre import Pauvre
from entities.plants.lumiere import Lumiere
from entities.plants.obscurite import Obscurite
from entities.plants.demi import Demi
from entities.group import Group
from meta_classes import entity_registry
import config
from logger import setup_logger

logger = setup_logger("main")


def create_empty_grid(width, height):
    return [[None for _ in range(width)] for _ in range(height)]


def spawn_animals(world, time_manager, entity_class, count):
    pauvre_groups = [Group(i) for i in range(1, 6)]
    malheureux_groups = [Group(i) for i in range(6, 11)]
    
    for _ in range(count):
        for _ in range(100):
            x = random.randint(0, world.width - 1)
            y = random.randint(0, world.height - 1)
            
            if entity_class.__name__ == 'Pauvre':
                group = random.choice(pauvre_groups)
            elif entity_class.__name__ == 'Malheureux':
                group = random.choice(malheureux_groups)

            if world.cells[y][x] is None:
                entity = entity_class(x, y, world, time_manager, group)
                world.place_entity(entity, x, y)
                group.add_member(entity)
                logger.info(f"Spawned {entity_class.__name__} at ({x}, {y}) in group {group.group_number}")
                break


def spawn_plants(world, time_manager, entity_class, count):
    for _ in range(count):
        for _ in range(100):
            x = random.randint(0, world.width - 1)
            y = random.randint(0, world.height - 1)

            if world.cells[y][x] is None:
                entity = entity_class(x, y, symbol=None, world=world, timer=time_manager)
                world.place_entity(entity, x, y)
                logger.info(f"Spawned {entity_class.__name__} at ({x}, {y})")
                break


def log_entity_counts(world):
    """Подсчитывает и логирует количество каждого типа сущностей в мире"""
    counts = {}
    for row in world.cells:
        for cell in row:
            if cell is not None:
                entity_type = type(cell).__name__
                if entity_type in counts:
                    counts[entity_type] += 1
                else:
                    counts[entity_type] = 1
    
    logger.info("--- Entity counts ---")
    for entity_type, count in counts.items():
        logger.info(f"{entity_type}: {count}")
    logger.info("---------------------")


def log_registry_info():
    """Логирует информацию о зарегистрированных классах в реестре"""
    logger.info("=== Entity Registry Information ===")
    logger.info("Registered Plants:")
    for name, cls in entity_registry['plants'].items():
        active_phases = getattr(cls, 'ACTIVE_PHASES', [])
        semi_active_phases = getattr(cls, 'SEMI_ACTIVE_PHASES', [])
        inactive_phases = getattr(cls, 'INACTIVE_PHASES', [])
        logger.info(f"  - {name}:")
        logger.info(f"    Active phases: {active_phases}")
        logger.info(f"    Semi-active phases: {semi_active_phases}")
        logger.info(f"    Inactive phases: {inactive_phases}")
    
    logger.info("Registered Animals:")
    for name, cls in entity_registry['animals'].items():
        active_phases = getattr(cls, 'ACTIVE_PHASES', [])
        food_sources = getattr(cls, 'FOOD_SOURCES', [])
        movement_pattern = getattr(cls, 'MOVEMENT_PATTERN', 'normal')
        reproduction_strategy = getattr(cls, 'REPRODUCTION_STRATEGY', 'same_group')
        behavior_traits = getattr(cls, 'BEHAVIOR_TRAITS', [])
        
        logger.info(f"  - {name}:")
        logger.info(f"    Active phases: {active_phases}")
        logger.info(f"    Food sources: {food_sources}")
        logger.info(f"    Movement pattern: {movement_pattern}")
        logger.info(f"    Reproduction strategy: {reproduction_strategy}")
        logger.info(f"    Behavior traits: {behavior_traits}")
    
    logger.info("===================================")


def main():
    logger.info("Starting ecosystem simulation with metaclasses")
    
    # Логирование информации о зарегистрированных классах
    log_registry_info()
    
    # Создание мира и таймера
    cells = create_empty_grid(config.GRID_WIDTH, config.GRID_HEIGHT)
    world = Grid(config.GRID_WIDTH, config.GRID_HEIGHT, cells)
    time_manager = TimeManager(config.TICKS_PER_PHASE)
    
    # Размещение растений
    spawn_plants(world, time_manager, Lumiere, config.INITIAL_LUMIERE_COUNT)
    spawn_plants(world, time_manager, Obscurite, config.INITIAL_OBSCURITE_COUNT)
    spawn_plants(world, time_manager, Demi, config.INITIAL_DEMI_COUNT)
    
    # Размещение животных
    spawn_animals(world, time_manager, Pauvre, config.INITIAL_PAUVRE_COUNT)
    spawn_animals(world, time_manager, Malheureux, config.INITIAL_MALHEUREUX_COUNT)
    
    # Логирование начального состояния
    log_entity_counts(world)
    
    # Главный цикл симуляции
    for tick in range(config.SIMULATION_TICKS):
        logger.info(f"\n\n=== Tick {tick + 1} | Time phase: {time_manager.current_phase} ===")
        world.tick()
        time_manager.advance_time()
        
        # Логирование каждые несколько тиков
        if (tick + 1) % 10 == 0:
            log_entity_counts(world)
    
    # Логирование финального состояния
    logger.info("\n=== Final state ===")
    log_entity_counts(world)
    logger.info("Simulation completed.")


if __name__ == "__main__":
    main()