from entities.animal import Animal

class Pauvre(Animal):
    """
    Животное Pauvre, которое активно днем и в сумеречное время
    """
    # Определяем активные фазы
    ACTIVE_PHASES = ['morning', 'day', 'evening']
    
    # Определяем источники пищи
    FOOD_SOURCES = ['Lumiere']
    
    # Определяем паттерн движения
    MOVEMENT_PATTERN = 'normal'  # normal, hungry, territorial
    
    # Определяем стратегию размножения
    REPRODUCTION_STRATEGY = 'same_group'  # same_group, different_group, any
    
    def __init__(self, x, y, world, timer, group):
        super().__init__(x, y, 'P', world, timer, group, ['Lumiere'], None, None)