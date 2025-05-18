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
import copy

logger = setup_logger("gui")

# Константы для интерфейса
CELL_SIZE = 30
CANVAS_WIDTH = GRID_WIDTH * CELL_SIZE
CANVAS_HEIGHT = GRID_HEIGHT * CELL_SIZE
MAX_SIMULATION_TICKS = 2000  # Максимальное количество тиков симуляции

# Цвета для различных типов сущностей
COLORS = {
    'Lumiere': '#FFFF00',    # Жёлтый для Lumiere
    'Obscurite': '#0000FF',  # Синий для Obscurite
    'Demi': '#808080',       # Серый для Demi
    'Pauvre': '#FFFF00',     # Жёлтый для Pauvre
    'Malheureux': '#800080'  # Фиолетовый для Malheureux
}

# Цвета для выделений
HIGHLIGHT_COLORS = {
    'action_cell': '#DDDDDD'  # Светло-серый цвет для клеток возможных действий
}

def create_empty_grid(width, height):
    return [[None for _ in range(width)] for _ in range(height)]

def setup_world():
    """Создает и инициализирует мир симуляции"""
    cells = create_empty_grid(GRID_WIDTH, GRID_HEIGHT)
    world = Grid(GRID_WIDTH, GRID_HEIGHT, cells)
    time_manager = TimeManager(ticks_per_phase=TICKS_PER_PHASE)  
    
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

def update_canvas(window, world, selected_entity=None):
    """Обновляет отображение мира на канвасе"""
    graph = window['-MAP-']
    graph.erase()
    
    # Отрисовываем сетку
    for x in range(0, CANVAS_WIDTH + 1, CELL_SIZE):
        graph.draw_line((x, 0), (x, CANVAS_HEIGHT), color='gray')
    for y in range(0, CANVAS_HEIGHT + 1, CELL_SIZE):
        graph.draw_line((0, y), (CANVAS_WIDTH, y), color='gray')
    
    # Если есть выбранное животное, подсвечиваем клетки действия
    action_cells = []
    if selected_entity and type(selected_entity).__name__ in ['Pauvre', 'Malheureux']:
        # Соседние клетки - потенциальные клетки действия
        action_cells = [(selected_entity.x + dx, selected_entity.y + dy) 
                         for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]
                         if 0 <= selected_entity.x + dx < world.width and 0 <= selected_entity.y + dy < world.height]
        
        # Сначала отрисовываем подсветку для клеток действия
        for ax, ay in action_cells:
            pixel_x = ax * CELL_SIZE
            pixel_y = ay * CELL_SIZE
            graph.draw_rectangle(
                (pixel_x, pixel_y),
                (pixel_x + CELL_SIZE, pixel_y + CELL_SIZE),
                fill_color=HIGHLIGHT_COLORS['action_cell'],
                line_color=None
            )
    
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
                    
                    # Если это выбранное животное - делаем обводку толще
                    line_width = 3 if entity == selected_entity else 1
                    
                    graph.draw_circle(
                        (center_x, center_y),
                        radius,
                        fill_color=COLORS[entity_type],
                        line_color='black',
                        line_width=line_width
                    )

def highlight_animal_and_actions(window, world, mouse_x, mouse_y):
    """Подсвечивает выбранное животное и клетки, куда оно может совершить действие"""
    graph = window['-MAP-']
    
    # Преобразуем координаты мыши в координаты сетки
    grid_x = int(mouse_x / CELL_SIZE)
    grid_y = int(mouse_y / CELL_SIZE)
    
    # Проверяем границы
    if 0 <= grid_x < world.width and 0 <= grid_y < world.height:
        entity = world.cells[grid_y][grid_x]
        if entity is not None and type(entity).__name__ in ['Pauvre', 'Malheureux']:
            # Получаем клетки, на которые может воздействовать животное
            action_cells = []
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = grid_x + dx, grid_y + dy
                if 0 <= nx < world.width and 0 <= ny < world.height:
                    action_cells.append((nx, ny))
            
            # Обновляем канвас с выделенным животным и клетками действия
            update_canvas(window, world, entity)
            
            # Добавляем информацию об окружении этого животного
            neighbors = world.get_neighbors(grid_x, grid_y)
            neighbor_info = f"Животное: {type(entity).__name__} в группе {entity.group.group_number}\n"
            neighbor_info += f"Голод: {entity.hunger}\n"
            neighbor_info += f"Активно: {'Да' if entity.timer.current_phase in getattr(entity, 'ACTIVE_PHASES', []) else 'Нет'}\n"
            neighbor_info += "\nВозможные действия на соседних клетках:\n"
            
            # Анализируем возможные действия
            for i, neighbor in enumerate(neighbors):
                cell, nx, ny = neighbor
                actions = []
                
                # Клетка для перемещения
                actions.append("Перемещение")
                
                # Проверка на еду
                if cell is not None:
                    cell_type = type(cell).__name__
                    if hasattr(entity, 'eatable_entities') and cell_type in getattr(entity, 'eatable_entities', []):
                        actions.append("Поедание")
                    
                    # Проверка на размножение
                    if cell_type == type(entity).__name__:
                        can_reproduce = False
                        try:
                            if entity.reproduce_condition and entity.reproduce_condition(entity, cell):
                                can_reproduce = True
                        except:
                            pass
                        
                        if can_reproduce:
                            actions.append("Размножение")
                        
                        # Проверка на формирование группы
                        if entity.group.aggression == 0 and cell.group.aggression == 0:
                            actions.append("Формирование группы")
                
                direction = ["Сверху", "Снизу", "Слева", "Справа"][i]
                neighbor_info += f"- {direction} ({nx}, {ny}): {', '.join(actions)}\n"
                if cell is not None:
                    neighbor_info += f"  Сущность: {type(cell).__name__}\n"
                else:
                    neighbor_info += f"  Пусто\n"
                    
            window['-INFO-'].update(neighbor_info)
            
            return entity
        else:
            window['-INFO-'].update("Выберите животное для просмотра информации")
            update_canvas(window, world)
    
    return None

def run_simulation_for_ticks(world, time_manager, target_tick, current_tick=0):
    """Запускает симуляцию на указанное количество тиков"""
    # Сохраняем текущее состояние в истории если нужно возвращаться назад
    ticks_to_run = target_tick - current_tick
    
    if ticks_to_run > 0:
        # Симуляция вперед
        for _ in range(ticks_to_run):
            world.tick()
            time_manager.advance_time()
    
    return world, time_manager, target_tick

def main():
    sg.theme('DefaultNoMoreNagging')  # Устанавливаем тему
    
    # Создаем макет окна
    layout = [
        [sg.Text('Тик симуляции:'), sg.Slider(range=(0, MAX_SIMULATION_TICKS), orientation='h', key='-TICKS-', enable_events=True, size=(50, 15))],
        [sg.Text('Текущая фаза:'), sg.Text('morning', size=(10, 1), key='-PHASE-')],
        [sg.Graph(canvas_size=(CANVAS_WIDTH, CANVAS_HEIGHT), 
                  graph_bottom_left=(0, 0), 
                  graph_top_right=(CANVAS_WIDTH, CANVAS_HEIGHT), 
                  key='-MAP-', 
                  enable_events=True,
                  background_color='white')],
        [sg.Text('Информация:', size=(15, 1)), sg.Multiline(size=(50, 8), key='-INFO-', disabled=True)],
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
    current_tick = 0
    selected_entity = None
    
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
            window['-TICKS-'].update(0)
            current_tick = 0
            update_canvas(window, world)
            window['-STATS-'].update(calculate_stats(world))
            window['-PHASE-'].update(time_manager.current_phase)
            
        if event == '-TICKS-':
            target_tick = int(values['-TICKS-'])
            
            # Обновляем симуляцию до нужного тика
            world, time_manager, current_tick = run_simulation_for_ticks(world, time_manager, target_tick, current_tick)
                
            window['-PHASE-'].update(time_manager.current_phase)
            
            # Обновляем отображение
            update_canvas(window, world, selected_entity)
            window['-STATS-'].update(calculate_stats(world))
            
        if event == '-MAP-':
            # Обработка клика мыши по карте для выбора животного
            mouse_x, mouse_y = values['-MAP-']
            selected_entity = highlight_animal_and_actions(window, world, mouse_x, mouse_y)
            
        if running:
            # Автоматическое обновление симуляции при работе
            speed = values['-SPEED-']
            
            # Увеличиваем тик
            current_tick += 1
            if current_tick > MAX_SIMULATION_TICKS:
                current_tick = MAX_SIMULATION_TICKS
                running = False
                window['-START-'].update(disabled=False)
                window['-PAUSE-'].update(disabled=True)
            
            window['-TICKS-'].update(current_tick)
            
            # Обновляем симуляцию
            world.tick()
            time_manager.advance_time()
            
            window['-PHASE-'].update(time_manager.current_phase)
            
            # Обновляем отображение
            if selected_entity and selected_entity.world:  # Проверяем, что выбранное животное все еще существует
                update_canvas(window, world, selected_entity)
            else:
                selected_entity = None
                update_canvas(window, world)
            
            window['-STATS-'].update(calculate_stats(world))
            
    window.close()

if __name__ == '__main__':
    main()