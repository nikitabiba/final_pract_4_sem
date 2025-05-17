from entities.plant import Plant

class Demi(Plant):
    """
    Растение, которое активно в сумеречное время (утро и вечер)
    """
    # Определяем активные, полуактивные и неактивные фазы
    ACTIVE_PHASES = ['morning', 'evening']
    SEMI_ACTIVE_PHASES = []
    INACTIVE_PHASES = ['day', 'night']
    
    def __init__(self, x, y, symbol, world, timer):
        super().__init__(x, y, "D", world, timer)