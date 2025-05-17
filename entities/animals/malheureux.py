from entities.animal import Animal

class Malheureux(Animal):
    """
    Животное Malheureux, которое активно в сумеречное время (утро и вечер)
    """
    # Определяем активные фазы
    ACTIVE_PHASES = ['morning', 'evening']
    
    # Определяем источники пищи
    FOOD_SOURCES = ['Demi', 'Obscurite', 'Pauvre']
    
    # Определяем паттерн движения
    MOVEMENT_PATTERN = 'hungry'  # normal, hungry, territorial
    
    # Определяем стратегию размножения
    REPRODUCTION_STRATEGY = 'different_group'  # same_group, different_group, any
    
    # Дополнительные поведенческие черты
    BEHAVIOR_TRAITS = ['cannibalism']
    
    def __init__(self, x, y, world, timer, group):
        super().__init__(x, y, 'M', world, timer, group, ['Demi', 'Obscurite', 'Pauvre'], None, None)