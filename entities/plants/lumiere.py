from entities.plant import Plant

class Lumiere(Plant):
    """
    Растение, которое активно днем и менее активно в сумеречное время (утро и вечер)
    """
    # Определяем активные, полуактивные и неактивные фазы
    ACTIVE_PHASES = ['day']
    SEMI_ACTIVE_PHASES = ['morning', 'evening']
    INACTIVE_PHASES = ['night']
    
    def __init__(self, x, y, symbol, world, timer):
        super().__init__(x, y, "L", world, timer)