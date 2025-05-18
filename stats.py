import PySimpleGUI as sg
from gui import setup_world, update_canvas, calculate_stats, update_simulation
from config import GRID_WIDTH, GRID_HEIGHT, SIMULATION_TICKS
from logger import setup_logger

logger = setup_logger("stats")

def get_detailed_stats(world):
    """
    Собирает детальную статистику о мире для отображения в GUI
    """
    # Количество каждого типа сущностей
    entity_counts = {}
    
    # Дополнительные метрики для животных
    animal_metrics = {
        'Pauvre': {
            'total_hunger': 0,
            'avg_hunger': 0,
            'group_sizes': {},
            'active_count': 0
        },
        'Malheureux': {
            'total_hunger': 0,
            'avg_hunger': 0,
            'group_sizes': {},
            'active_count': 0
        }
    }
    
    # Счетчики для растений
    plant_metrics = {
        'Lumiere': {'growing': 0, 'dormant': 0},
        'Obscurite': {'growing': 0, 'dormant': 0},
        'Demi': {'growing': 0, 'dormant': 0}
    }
    
    # Собираем данные
    for row in world.cells:
        for cell in row:
            if cell is not None:
                entity_type = type(cell).__name__
                
                # Обновляем базовые счетчики
                if entity_type in entity_counts:
                    entity_counts[entity_type] += 1
                else:
                    entity_counts[entity_type] = 1
                
                # Собираем метрики для животных
                if entity_type in ['Pauvre', 'Malheureux']:
                    animal_metrics[entity_type]['total_hunger'] += cell.hunger
                    
                    # Счетчик групп
                    group_num = cell.group.group_number
                    if group_num in animal_metrics[entity_type]['group_sizes']:
                        animal_metrics[entity_type]['group_sizes'][group_num] += 1
                    else:
                        animal_metrics[entity_type]['group_sizes'][group_num] = 1
                    
                    # Счетчик активных животных
                    if cell.timer.current_phase in getattr(cell, 'ACTIVE_PHASES', []):
                        animal_metrics[entity_type]['active_count'] += 1
                
                # Собираем метрики для растений
                if entity_type in ['Lumiere', 'Obscurite', 'Demi']:
                    if cell.is_growing:
                        plant_metrics[entity_type]['growing'] += 1
                    else:
                        plant_metrics[entity_type]['dormant'] += 1
    
    # Вычисляем средние значения
    for animal_type in animal_metrics:
        count = entity_counts.get(animal_type, 0)
        if count > 0:
            animal_metrics[animal_type]['avg_hunger'] = animal_metrics[animal_type]['total_hunger'] / count
    
    # Форматируем вывод
    stats_text = "Статистика популяции:\n\n"
    
    # Общие счетчики сущностей
    stats_text += "Количество сущностей:\n"
    for entity_type, count in entity_counts.items():
        stats_text += f"{entity_type}: {count}\n"
    
    stats_text += "\nСтатистика животных:\n"
    for animal_type, metrics in animal_metrics.items():
        count = entity_counts.get(animal_type, 0)
        if count > 0:
            stats_text += f"{animal_type}:\n"
            stats_text += f"  Средний голод: {metrics['avg_hunger']:.1f}\n"
            stats_text += f"  Активных: {metrics['active_count']} из {count}\n"
            
            # Информация о группах
            stats_text += f"  Группы: "
            group_info = []
            for group_num, size in metrics['group_sizes'].items():
                group_info.append(f"[Группа {group_num}: {size}]")
            stats_text += ", ".join(group_info) + "\n"
    
    stats_text += "\nСтатистика растений:\n"
    for plant_type, metrics in plant_metrics.items():
        count = entity_counts.get(plant_type, 0)
        if count > 0:
            stats_text += f"{plant_type}:\n"
            stats_text += f"  Растущих: {metrics['growing']} ({metrics['growing']/count*100:.1f}%)\n"
            stats_text += f"  Спящих: {metrics['dormant']} ({metrics['dormant']/count*100:.1f}%)\n"
    
    return stats_text

def get_current_time_info(time_value):
    """
    Возвращает информацию о текущем времени в зависимости от значения ползунка
    """
    # Определяем фазу
    if 0 <= time_value <= 6:
        phase = 'morning'
        time_str = f"Утро (6:00-12:00) - {int(time_value)}:00"
    elif 6 < time_value <= 12:
        phase = 'day'
        time_str = f"День (12:00-18:00) - {int(time_value)}:00"
    elif 12 < time_value <= 18:
        phase = 'evening'
        time_str = f"Вечер (18:00-24:00) - {int(time_value)}:00"
    else:
        phase = 'night'
        time_str = f"Ночь (0:00-6:00) - {int(time_value)}:00"
    
    # Активность существ в данную фазу
    activity_info = {
        'morning': {
            'active': ['Pauvre', 'Malheureux'],
            'growing': ['Demi'],
            'semi_active': ['Lumiere', 'Obscurite']
        },
        'day': {
            'active': ['Pauvre'],
            'growing': ['Lumiere'],
            'semi_active': []
        },
        'evening': {
            'active': ['Pauvre', 'Malheureux'],
            'growing': ['Demi'],
            'semi_active': ['Lumiere', 'Obscurite']
        },
        'night': {
            'active': [],
            'growing': ['Obscurite'],
            'semi_active': []
        }
    }
    
    info = f"{time_str} ({phase})\n\n"
    info += "Активные существа:\n"
    
    active_list = activity_info[phase]['active']
    if active_list:
        info += ", ".join(active_list) + "\n"
    else:
        info += "Нет активных животных\n"
    
    info += "\nРастущие растения:\n"
    growing_list = activity_info[phase]['growing']
    if growing_list:
        info += ", ".join(growing_list) + "\n"
    else:
        info += "Нет активных растений\n"
    
    info += "\nПолуактивные растения:\n"
    semi_active_list = activity_info[phase]['semi_active']
    if semi_active_list:
        info += ", ".join(semi_active_list) + "\n"
    else:
        info += "Нет полуактивных растений\n"
    
    return info