from entities.plant import Plant

class Obscurite(Plant):
    """
    Растение, которое активно ночью и менее активно в сумеречное время (утро и вечер)
    """
    # Определяем активные, полуактивные и неактивные фазы
    ACTIVE_PHASES = ['night']
    SEMI_ACTIVE_PHASES = ['morning', 'evening']
    INACTIVE_PHASES = ['day']
    
    def __init__(self, x, y, symbol, world, timer):
        super().__init__(x, y, "O", world, timer)