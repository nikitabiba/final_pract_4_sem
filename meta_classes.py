from logger import setup_logger
import types
import copy
import random

logger = setup_logger(__name__)

# Глобальный реестр для регистрации всех классов экосистемы
entity_registry = {
    'plants': {},
    'animals': {}
}

class EcosystemMeta(type):
    """
    Базовый метакласс для сущностей в экосистеме
    """
    def __new__(mcs, name, bases, attrs):
        # Создаем новый класс
        cls = super().__new__(mcs, name, bases, attrs)
        
        # Регистрируем класс в соответствующем реестре
        if name != 'Plant' and name != 'Animal':
            if 'Plant' in [base.__name__ for base in bases]:
                entity_registry['plants'][name] = cls
                logger.debug(f"Registered Plant class: {name}")
            elif 'Animal' in [base.__name__ for base in bases]:
                entity_registry['animals'][name] = cls
                logger.debug(f"Registered Animal class: {name}")
        
        return cls


class EvalPlantMeta(EcosystemMeta):
    """
    Метакласс для растений, который инжектирует методы в зависимости от текущего состояния среды
    """
    def __new__(mcs, name, bases, attrs):
        # Определяем поведение роста и активности по фазам дня
        if name != 'Plant':
            active_phases = attrs.get('ACTIVE_PHASES', [])
            semi_active_phases = attrs.get('SEMI_ACTIVE_PHASES', [])
            inactive_phases = attrs.get('INACTIVE_PHASES', [])
            
            def grow(self):
                if self.timer.current_phase in active_phases:
                    self.is_growing = True
                    self.active = 1
                elif self.timer.current_phase in inactive_phases:
                    self.is_growing = False
                    self.active = 0
                else:
                    self.is_growing = True
                    self.active = 0.5
                
                if self.is_growing:
                    if self.world is not None:
                        neighbors = self.world.get_neighbors(self.x, self.y)
                        for neighbor in neighbors:
                            if neighbor[0] is not None and isinstance(neighbor[0], type(bases[0])):
                                if type(self) != type(neighbor[0]):
                                    captured = random.choices(
                                        [True, False], 
                                        weights=[0.5 + 0.25*self.active - 0.25*neighbor[0].active, 
                                                0.5 - 0.25*self.active + 0.25*neighbor[0].active]
                                    )[0]
                                    
                                    if captured:
                                        x, y = neighbor[0].x, neighbor[0].y
                                        logger.debug(f"Plant {self.symbol} at ({self.x}, {self.y}) captured {neighbor[0].symbol} at ({x}, {y})")
                                        self.world.remove_entity(neighbor[0])
                                        self.world.duplicate_entity(self, x, y)
                            elif neighbor[0] is None:
                                logger.debug(f"Plant {self.symbol} at ({self.x}, {self.y}) spread to empty space at ({neighbor[1]}, {neighbor[2]})")
                                self.world.duplicate_entity(self, neighbor[1], neighbor[2])
                            break

            def act(self):
                self.grow()
            
            # Инжектируем методы
            attrs['grow'] = grow
            attrs['act'] = act
        
        # Создаем новый класс с модифицированными методами
        return super().__new__(mcs, name, bases, attrs)


class EvalAnimalMeta(EcosystemMeta):
    """
    Метакласс для животных, который инжектирует методы в зависимости от текущего состояния среды
    """
    def __new__(mcs, name, bases, attrs):
        if name != 'Animal':
            # Получаем информацию о поведении животного из атрибутов класса
            active_phases = attrs.get('ACTIVE_PHASES', [])
            food_sources = attrs.get('FOOD_SOURCES', [])
            movement_pattern = attrs.get('MOVEMENT_PATTERN', 'normal')
            reproduction_strategy = attrs.get('REPRODUCTION_STRATEGY', 'same_group')
            \
            if reproduction_strategy == 'same_group':
                attrs['reproduce_condition'] = lambda n1, n2: n1.group == n2.group
            elif reproduction_strategy == 'different_group':
                attrs['reproduce_condition'] = lambda n1, n2: n1.group != n2.group
            else:  # any
                attrs['reproduce_condition'] = lambda n1, n2: True
                
            if 'cannibalism' in attrs.get('BEHAVIOR_TRAITS', []):
                attrs['eat_condition'] = lambda n1, n2: type(n1) == type(n2) and n1.group != n2.group and n2.group.aggression == 0
            else:
                attrs['eat_condition'] = lambda n1, n2: type(n1) == type(n2) and n1.group == n2.group
            
            def move(self):
                if movement_pattern == 'hungry' and self.hunger < 50:
                    if random.choice([0, 1, 2]) == 0:
                        direction = random.choice([(-1, 0), (1, 0), (0, -1), (0, 1)])
                        if self.x is not None and self.y is not None:
                            new_x, new_y = self.x + direction[0], self.y + direction[1]
                            logger.debug(f"Animal {self.symbol} at ({self.x}, {self.y}) moved to ({new_x}, {new_y}).")
                            self.world.move_entity(self, new_x, new_y)
                else:
                    direction = random.choice([(-1, 0), (1, 0), (0, -1), (0, 1)])
                    if self.x is not None and self.y is not None:
                        new_x, new_y = self.x + direction[0], self.y + direction[1]
                        logger.debug(f"Animal {self.symbol} at ({self.x}, {self.y}) moved to ({new_x}, {new_y}).")
                        self.world.move_entity(self, new_x, new_y)
            
            def eat(self):
                if self.timer.current_phase not in active_phases:
                    if random.choice([0, 1, 2]) == 0:
                        neighbors = self.world.get_neighbors(self.x, self.y)
                        for neighbor in neighbors:
                            if (neighbor[0] is not None and 
                                (type(neighbor[0]).__name__ in food_sources or 
                                (self.group.aggression == 1 and self.eat_condition(self, neighbor[0])))):
                                logger.debug(f"Animal {self.symbol} at ({self.x}, {self.y}) ate entity at ({neighbor[0].x}, {neighbor[0].y}).")
                                self.world.remove_entity(neighbor[0])
                                if isinstance(neighbor[0], type(bases[0])):
                                    neighbor[0].group.remove_member(neighbor[0])
                                self.hunger += 50
                                break
                else:
                    neighbors = self.world.get_neighbors(self.x, self.y)
                    for neighbor in neighbors:
                        if (neighbor[0] is not None and 
                            (type(neighbor[0]).__name__ in food_sources or 
                            (self.group.aggression == 1 and self.eat_condition(self, neighbor[0])))):
                            logger.debug(f"Animal {self.symbol} at ({self.x}, {self.y}) ate entity at ({neighbor[0].x}, {neighbor[0].y}).")
                            self.world.remove_entity(neighbor[0])
                            if isinstance(neighbor[0], type(bases[0])):
                                neighbor[0].group.remove_member(neighbor[0])
                            self.hunger += 50
                            break
            
            def reproduce(self):
                if self.world is not None:
                    neighbors = self.world.get_neighbors(self.x, self.y)
                    for neighbor in neighbors:
                        if (type(neighbor[0]) == type(self) and 
                            self.group.aggression == 0 and 
                            neighbor[0].group.aggression == 0 and 
                            self.reproduce_condition(self, neighbor[0])):
                            for n in neighbors:
                                if n[0] is None:
                                    new_entity = copy.deepcopy(self)
                                    self.group.add_member(new_entity)
                                    new_entity.hunger = 100
                                    self.world.place_entity(new_entity, n[1], n[2])
                                    logger.debug(f"Animal {self.symbol} at ({self.x}, {self.y}) reproduced with animal at ({neighbor[0].x}, {neighbor[0].y}) and animal at ({new_entity.x}, {new_entity.y}) was born.")
                                    break
            
            def form_group(self):
                neighbors = self.world.get_neighbors(self.x, self.y)
                for neighbor in neighbors:
                    if (type(neighbor[0]) == type(self) and 
                        self.group.aggression == 0 and 
                        neighbor[0].group.aggression == 0):
                        new_group = random.choice([self.group, neighbor[0].group])
                        if self.group != new_group:
                            neighbor[0].group.add_member(self)
                            self.group.remove_member(self)
                        else:
                            self.group.add_member(neighbor[0])
                            neighbor[0].group.remove_member(neighbor[0])
                        logger.debug(f"Animal {self.symbol} at ({self.x}, {self.y}) formed a group {new_group.group_number} with animal at ({neighbor[0].x}, {neighbor[0].y}).")
                        break
            
            def act(self):
                if self.timer.current_phase in active_phases:
                    if self.hunger < 50:
                        self.group.aggression = 1
                    if self.group.get_group_size() > 10:
                        self.group.split()
                    
                    action = random.choice(["move", "eat", "reproduce", "form_group"])
                    if action == "move":
                        self.move()
                    elif action == "eat":
                        self.eat()
                    elif action == "reproduce":
                        self.reproduce()
                    elif action == "form_group":
                        self.form_group()
                    
                    self.move()
                    
                    self.hunger -= 1
                    if self.hunger <= 0:
                        logger.debug(f"Animal {self.symbol} at ({self.x}, {self.y}) died.")
                        self.world.remove_entity(self)
                        self.group.remove_member(self)
            
            # Инжектируем сгенерированные методы в класс
            attrs['move'] = move
            attrs['eat'] = eat
            attrs['reproduce'] = reproduce
            attrs['form_group'] = form_group
            attrs['act'] = act
        
        # Создаем класс с модифицированными методами
        return super().__new__(mcs, name, bases, attrs)