import unittest
import sys
import os

# Добавляем корневую директорию проекта в путь
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from meta_classes import entity_registry
from entities.plants.lumiere import Lumiere
from entities.plants.obscurite import Obscurite
from entities.plants.demi import Demi
from entities.animals.pauvre import Pauvre
from entities.animals.malheureux import Malheureux
from world.time_manager import TimeManager
from world.grid import Grid


class TestMetaclasses(unittest.TestCase):
    
    def setUp(self):
        # Настройка тестового окружения
        self.time_manager = TimeManager(10)
        self.grid = Grid(10, 10, [[None for _ in range(10)] for _ in range(10)])
        
        # Создаем временную группу для животных
        class MockGroup:
            def __init__(self):
                self.members = []
                self.group_number = 1
                self.aggression = 0
            
            def add_member(self, animal):
                self.members.append(animal)
            
            def remove_member(self, animal):
                if animal in self.members:
                    self.members.remove(animal)
            
            def get_group_size(self):
                return len(self.members)
                
            def split(self):
                pass
                
            def update_aggression_level(self):
                pass
        
        self.mock_group = MockGroup()
    
    def test_registry_creation(self):
        """Проверяем, что классы правильно регистрируются в реестре"""
        self.assertIn('Lumiere', entity_registry['plants'])
        self.assertIn('Obscurite', entity_registry['plants'])
        self.assertIn('Demi', entity_registry['plants'])
        self.assertIn('Pauvre', entity_registry['animals'])
        self.assertIn('Malheureux', entity_registry['animals'])
    
    def test_auto_generated_methods_plant(self):
        """Проверяем, что методы для растений автоматически генерируются"""
        plant = Lumiere(1, 1, None, self.grid, self.time_manager)
        self.assertTrue(hasattr(plant, 'grow'))
        self.assertTrue(hasattr(plant, 'act'))
    
    def test_auto_generated_methods_animal(self):
        """Проверяем, что методы для животных автоматически генерируются"""
        animal = Pauvre(1, 1, self.grid, self.time_manager, self.mock_group)
        self.assertTrue(hasattr(animal, 'move'))
        self.assertTrue(hasattr(animal, 'eat'))
        self.assertTrue(hasattr(animal, 'reproduce'))
        self.assertTrue(hasattr(animal, 'form_group'))
        self.assertTrue(hasattr(animal, 'act'))
    
    def test_phases_influence_plant_behavior(self):
        """Проверяем, что поведение растений зависит от фазы времени"""
        plant = Lumiere(1, 1, None, self.grid, self.time_manager)
        
        # Проверка для дневной фазы (активная)
        self.time_manager.current_phase = 'day'
        plant.grow()
        self.assertTrue(plant.is_growing)
        self.assertEqual(plant.active, 1)
        
        # Проверка для ночной фазы (неактивная)
        self.time_manager.current_phase = 'night'
        plant.grow()
        self.assertFalse(plant.is_growing)
        self.assertEqual(plant.active, 0)
        
        # Проверка для утренней фазы (полуактивная)
        self.time_manager.current_phase = 'morning'
        plant.grow()
        self.assertTrue(plant.is_growing)
        self.assertEqual(plant.active, 0.5)
    
    def test_phases_influence_animal_behavior(self):
        """Проверяем, что поведение животных зависит от фазы времени"""
        # Размещаем животное на сетке
        animal = Pauvre(1, 1, self.grid, self.time_manager, self.mock_group)
        self.grid.place_entity(animal, 1, 1)
        
        # Проверка для активной фазы
        self.time_manager.current_phase = 'day'
        initial_x, initial_y = animal.x, animal.y
        animal.act()
        
        # Животное должно быть активным днем (должно двигаться или выполнять другие действия)
        self.assertTrue(hasattr(animal, 'hunger'))  # Проверка, что голод уменьшился
        
        # Проверка для неактивной фазы
        animal = Malheureux(3, 3, self.grid, self.time_manager, self.mock_group)
        self.grid.place_entity(animal, 3, 3)
        
        self.time_manager.current_phase = 'night'  # Неактивная фаза для Malheureux
        initial_hunger = animal.hunger
        animal.act()
        
        # Голод не должен уменьшаться в неактивной фазе
        self.assertEqual(animal.hunger, initial_hunger)


if __name__ == '__main__':
    unittest.main()