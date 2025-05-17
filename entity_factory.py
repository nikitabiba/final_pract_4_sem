from meta_classes import EvalPlantMeta, EvalAnimalMeta
from entities.plant import Plant
from entities.animal import Animal
from logger import setup_logger

logger = setup_logger(__name__)

def create_plant_class(name, symbol, active_phases, inactive_phases, semi_active_phases=None):
    """
    Динамически создает новый класс растения с указанными параметрами
    
    Аргументы:
        name: Имя класса
        symbol: Символ для отображения на карте
        active_phases: Список активных фаз дня
        inactive_phases: Список неактивных фаз дня
        semi_active_phases: Список полуактивных фаз дня (опционально)
    
    Возвращает:
        Новый класс растения
    """
    if semi_active_phases is None:
        semi_active_phases = []
    
    # Определяем атрибуты класса
    attrs = {
        'ACTIVE_PHASES': active_phases,
        'INACTIVE_PHASES': inactive_phases,
        'SEMI_ACTIVE_PHASES': semi_active_phases,
        '__init__': lambda self, x, y, symbol_param, world, timer: 
            Plant.__init__(self, x, y, symbol, world, timer)
    }
    
    # Создаем новый класс с использованием метакласса , metaclass=EvalPlantMeta
    new_plant_class = type(name, (Plant,), attrs)
    
    logger.info(f"Dynamically created new plant class: {name}")
    return new_plant_class


def create_animal_class(name, symbol, active_phases, food_sources, 
                      movement_pattern='normal', reproduction_strategy='same_group', 
                      behavior_traits=None):
    """
    Динамически создает новый класс животного с указанными параметрами
    
    Аргументы:
        name: Имя класса
        symbol: Символ для отображения на карте
        active_phases: Список активных фаз дня
        food_sources: Список источников пищи (имена классов)
        movement_pattern: Паттерн движения ('normal', 'hungry', 'territorial')
        reproduction_strategy: Стратегия размножения ('same_group', 'different_group', 'any')
        behavior_traits: Список поведенческих черт (опционально)
    
    Возвращает:
        Новый класс животного
    """
    if behavior_traits is None:
        behavior_traits = []
    
    # Определяем атрибуты класса
    attrs = {
        'ACTIVE_PHASES': active_phases,
        'FOOD_SOURCES': food_sources,
        'MOVEMENT_PATTERN': movement_pattern,
        'REPRODUCTION_STRATEGY': reproduction_strategy,
        'BEHAVIOR_TRAITS': behavior_traits,
        '__init__': lambda self, x, y, world, timer, group: 
            Animal.__init__(self, x, y, symbol, world, timer, group, food_sources, None, None)
    }
    
    # Создаем новый класс с использованием метакласса , metaclass=EvalAnimalMeta
    new_animal_class = type(name, (Animal,), attrs)
    
    logger.info(f"Dynamically created new animal class: {name}")
    return new_animal_class