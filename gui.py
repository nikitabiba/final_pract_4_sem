import PySimpleGUI as sg
import random
from config import GRID_WIDTH, GRID_HEIGHT, SIMULATION_TICKS, INITIAL_LUMIERE_COUNT, INITIAL_OBSCURITE_COUNT, INITIAL_DEMI_COUNT, INITIAL_PAUVRE_COUNT, INITIAL_MALHEUREUX_COUNT, TICKS_PER_PHASE
from world.grid import Grid
from world.time_manager import TimeManager
from entities.animals.malheureux import Malheureux
from entities.animals.pauvre import Pauvre
from entities.plants.lumiere import Lumiere
from entities.plants.obscurite import Obscurite
from entities.plants.demi import Demi
from entities.group import Group
from logger import setup_logger

logger = setup_logger("gui")

# Константы для интерфейса
CELL_SIZE = 30
CANVAS_WIDTH = GRID_WIDTH * CELL_SIZE
CANVAS_HEIGHT = GRID_HEIGHT * CELL_SIZE
MAX_TIME = 24  # 24 часа для симуляции полного дня

# Цвета для различных типов сущностей
COLORS = {
    'Lumiere': '#FFFF00',    # Жёлтый для Lumiere
    'Obscurite': '#0000FF',  # Синий для Obscurite
    'Demi': '#808080',       # Серый для Demi
    'Pauvre': '#FFFF00',     # Жёлтый для Pauvre
    'Malheureux': '#800080'  # Фиолетовый для Malheureux
}

def create_empty_grid(width, height):
    return [[None for _ in range(width)] for _ in range(height)]

def setup_world():
    """Создает и инициализирует мир симуляции"""
    cells = create_empty_grid(GRID_WIDTH, GRID_HEIGHT)
    world = Grid(GRID_WIDTH, GRID_HEIGHT, cells)
    time_manager = TimeManager(ticks_per_phase=TICKS_PER_PHASE)  # 2 тика на фазу
    
    # Создаем группы для животных
    pauvre_groups = [Group(i) for i in range(1, 11)]
    malheureux_groups = [Group(i) for i in range(11, 21)]
    
    # Размещаем растения
    spawn_plants(world, time_manager, Lumiere, INITIAL_LUMIERE_COUNT)
    spawn_plants(world, time_manager, Obscurite, INITIAL_OBSCURITE_COUNT)
    spawn_plants(world, time_manager, Demi, INITIAL_DEMI_COUNT)
    
    # Размещаем животных
    spawn_animals(world, time_manager, Pauvre, pauvre_groups, INITIAL_PAUVRE_COUNT)
    spawn_animals(world, time_manager, Malheureux, malheureux_groups, INITIAL_MALHEUREUX_COUNT)
    
    return world, time_manager

def spawn_plants(world, time_manager, entity_class, count):
    for _ in range(count):
        for _ in range(100):  # Пробуем найти пустую клетку
            x = random.randint(0, world.width - 1)
            y = random.randint(0, world.height - 1)
            
            if world.cells[y][x] is None:
                entity = entity_class(x, y, symbol=None, world=world, timer=time_manager)
                world.place_entity(entity, x, y)
                logger.info(f"Spawned {entity_class.__name__} at ({x}, {y})")
                break

def spawn_animals(world, time_manager, entity_class, groups, count):
    for _ in range(count):
        for _ in range(100):  # Пробуем найти пустую клетку
            x = random.randint(0, world.width - 1)
            y = random.randint(0, world.height - 1)
            
            group = random.choice(groups)
            
            if world.cells[y][x] is None:
                entity = entity_class(x, y, world, time_manager, group)
                world.place_entity(entity, x, y)
                group.add_member(entity)
                logger.info(f"Spawned {entity_class.__name__} at ({x}, {y}) in group {group.group_number}")
                break

def calculate_stats(world):
    """Подсчитывает статистику по количеству сущностей в мире"""
    counts = {}
    for row in world.cells:
        for cell in row:
            if cell is not None:
                entity_type = type(cell).__name__
                if entity_type in counts:
                    counts[entity_type] += 1
                else:
                    counts[entity_type] = 1
    
    # Форматируем статистику для отображения
    stats_text = "Статистика популяции:\n"
    for entity_type, count in counts.items():
        stats_text += f"{entity_type}: {count}\n"
    
    return stats_text

def update_canvas(window, world):
    """Обновляет отображение мира на канвасе"""
    graph = window['-MAP-']
    graph.erase()
    
    # Отрисовываем сетку
    for x in range(0, CANVAS_WIDTH + 1, CELL_SIZE):
        graph.draw_line((x, 0), (x, CANVAS_HEIGHT), color='gray')
    for y in range(0, CANVAS_HEIGHT + 1, CELL_SIZE):
        graph.draw_line((0, y), (CANVAS_WIDTH, y), color='gray')
    
    # Отрисовываем сущности
    for y in range(world.height):
        for x in range(world.width):
            entity = world.cells[y][x]
            if entity is not None:
                entity_type = type(entity).__name__
                pixel_x = x * CELL_SIZE
                pixel_y = y * CELL_SIZE
                
                # Отрисовка в зависимости от типа
                if entity_type in ['Lumiere', 'Obscurite', 'Demi']:
                    # Растения отображаются квадратами
                    graph.draw_rectangle(
                        (pixel_x, pixel_y), 
                        (pixel_x + CELL_SIZE, pixel_y + CELL_SIZE),
                        fill_color=COLORS[entity_type],
                        line_color='black'
                    )
                else:
                    # Животные отображаются кругами
                    # Размер круга зависит от "масштаба" (условно от уровня голода)
                    scale = 1.0
                    if hasattr(entity, 'hunger'):
                        scale = min(1.0, entity.hunger / 100.0)
                    
                    radius = (CELL_SIZE / 2) * scale
                    center_x = pixel_x + CELL_SIZE / 2
                    center_y = pixel_y + CELL_SIZE / 2
                    
                    graph.draw_circle(
                        (center_x, center_y),
                        radius,
                        fill_color=COLORS[entity_type],
                        line_color='black'
                    )

def highlight_vision_radius(window, world, mouse_x, mouse_y):
    """Подсвечивает радиус обзора выбранного животного"""
    graph = window['-MAP-']
    
    # Преобразуем координаты мыши в координаты сетки
    grid_x = int(mouse_x / CELL_SIZE)
    grid_y = int(mouse_y / CELL_SIZE)
    
    # Проверяем границы
    if 0 <= grid_x < world.width and 0 <= grid_y < world.height:
        entity = world.cells[grid_y][grid_x]
        if entity is not None and type(entity).__name__ in ['Pauvre', 'Malheureux']:
            # Подсвечиваем радиус обзора для животного
            # Считаем, что радиус обзора - 1 клетка (можно изменить)
            vision_radius = 1
            
            for y_offset in range(-vision_radius, vision_radius + 1):
                for x_offset in range(-vision_radius, vision_radius + 1):
                    nx, ny = grid_x + x_offset, grid_y + y_offset
                    if 0 <= nx < world.width and 0 <= ny < world.height:
                        pixel_x = nx * CELL_SIZE
                        pixel_y = ny * CELL_SIZE
                        
                        # Полупрозрачный круг для области обзора
                        graph.draw_rectangle(
                            (pixel_x, pixel_y),
                            (pixel_x + CELL_SIZE, pixel_y + CELL_SIZE),
                            fill_color='#FFFF0055',  # Полупрозрачный жёлтый
                            line_color=None
                        )
            
            # Добавим информацию об окружении этого животного
            neighbors = world.get_neighbors(grid_x, grid_y)
            neighbor_info = f"Животное: {type(entity).__name__} в группе {entity.group.group_number}\n"
            neighbor_info += f"Голод: {entity.hunger}\n"
            neighbor_info += "Соседи:\n"
            
            for neighbor in neighbors:
                if neighbor[0] is not None:
                    neighbor_info += f"- {type(neighbor[0]).__name__} на ({neighbor[1]}, {neighbor[2]})\n"
                else:
                    neighbor_info += f"- Пусто на ({neighbor[1]}, {neighbor[2]})\n"
                    
            window['-INFO-'].update(neighbor_info)
        else:
            window['-INFO-'].update("Выберите животное для просмотра информации")

def update_simulation(world, time_manager, time_value):
    """Обновляет состояние симуляции в соответствии с положением ползунка времени"""
    # Пересчитываем фазу времени на основе значения ползунка
    if 0 <= time_value <= 6:
        time_manager.current_phase = 'morning'
    elif 6 < time_value <= 12:
        time_manager.current_phase = 'day'
    elif 12 < time_value <= 18:
        time_manager.current_phase = 'evening'
    else:
        time_manager.current_phase = 'night'
    
    # Выполняем один шаг симуляции
    world.tick()
    
    return world, time_manager

def main():
    sg.theme('DefaultNoMoreNagging')  # Устанавливаем тему
    
    # Создаем макет окна
    layout = [
        [sg.Text('Время суток:'), sg.Slider(range=(0, MAX_TIME), orientation='h', key='-TIME-', enable_events=True, size=(50, 15))],
        [sg.Text('Текущая фаза:'), sg.Text('morning', size=(10, 1), key='-PHASE-')],
        [sg.Graph(canvas_size=(CANVAS_WIDTH, CANVAS_HEIGHT), 
                  graph_bottom_left=(0, 0), 
                  graph_top_right=(CANVAS_WIDTH, CANVAS_HEIGHT), 
                  key='-MAP-', 
                  enable_events=True,
                  background_color='white')],
        [sg.Text('Информация:', size=(15, 1)), sg.Multiline(size=(50, 5), key='-INFO-', disabled=True)],
        [sg.Multiline(size=(70, 10), key='-STATS-', disabled=True)],
        [sg.Button('Запустить симуляцию', key='-START-'), 
         sg.Button('Пауза', key='-PAUSE-', disabled=True),
         sg.Button('Сброс', key='-RESET-'),
         sg.Text('Скорость:'), 
         sg.Slider(range=(1, 10), default_value=5, orientation='h', key='-SPEED-', size=(20, 15))]
    ]
    
    window = sg.Window('Ecosystem Simulator', layout, finalize=True, resizable=True)
    
    # Инициализируем мир
    world, time_manager = setup_world()
    update_canvas(window, world)
    window['-STATS-'].update(calculate_stats(world))
    
    # Переменные для управления симуляцией
    running = False
    speed = 5  # Скорость симуляции (обновлений в секунду)
    last_time = 0
    
    # Основной цикл обработки событий
    while True:
        event, values = window.read(timeout=100 if running else None)
        
        if event == sg.WINDOW_CLOSED:
            break
            
        if event == '-START-':
            running = True
            window['-START-'].update(disabled=True)
            window['-PAUSE-'].update(disabled=False)
            
        if event == '-PAUSE-':
            running = False
            window['-START-'].update(disabled=False)
            window['-PAUSE-'].update(disabled=True)
            
        if event == '-RESET-':
            running = False
            window['-START-'].update(disabled=False)
            window['-PAUSE-'].update(disabled=True)
            world, time_manager = setup_world()
            window['-TIME-'].update(0)
            update_canvas(window, world)
            window['-STATS-'].update(calculate_stats(world))
            window['-PHASE-'].update(time_manager.current_phase)
            
        if event == '-TIME-':
            time_value = int(values['-TIME-'])
            
            # Обновляем фазу на основе значения ползунка
            if 0 <= time_value <= 6:
                time_manager.current_phase = 'morning'
            elif 6 < time_value <= 12:
                time_manager.current_phase = 'day'
            elif 12 < time_value <= 18:
                time_manager.current_phase = 'evening'
            else:
                time_manager.current_phase = 'night'
                
            window['-PHASE-'].update(time_manager.current_phase)
            
            # Обновляем симуляцию и отображение
            world, time_manager = update_simulation(world, time_manager, time_value)
            update_canvas(window, world)
            window['-STATS-'].update(calculate_stats(world))
            
        if event == '-MAP-':
            # Обработка движения мыши по карте
            mouse_x, mouse_y = values['-MAP-']
            highlight_vision_radius(window, world, mouse_x, mouse_y)
            
        if running:
            # Автоматическое обновление симуляции при работе
            speed = values['-SPEED-']
            current_time = values['-TIME-']
            
            # Увеличиваем время
            new_time = (current_time + speed/50) % MAX_TIME
            window['-TIME-'].update(new_time)
            
            # Обновляем фазу на основе нового значения времени
            if 0 <= new_time <= 6:
                time_manager.current_phase = 'morning'
            elif 6 < new_time <= 12:
                time_manager.current_phase = 'day'
            elif 12 < new_time <= 18:
                time_manager.current_phase = 'evening'
            else:
                time_manager.current_phase = 'night'
                
            window['-PHASE-'].update(time_manager.current_phase)
            
            # Обновляем симуляцию и отображение
            world, time_manager = update_simulation(world, time_manager, new_time)
            update_canvas(window, world)
            window['-STATS-'].update(calculate_stats(world))
            
    window.close()

if __name__ == '__main__':
    main()