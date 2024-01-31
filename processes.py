from matplotlib.patches import FancyArrowPatch, ArrowStyle
import numpy as np
from scipy.interpolate import interp1d


class Process:
    def __init__(self): # Общие атрибуты для всех процессов
        self.start = None
        self.end = None
        self.color = 'k'
        self.arrow_params = {}  # Инициализация пустым словарем
        self.dots_params = {'start': None, 'end': None}
        self.linestyle = '-'
        self.linewidth = 2.5
        self.extra_lines = []  # Для хранения инструкций по рисованию дополнительных линий
        self.xtick_labels = []
        self.ytick_labels = []
        #self.drawing = None  # Инициализируем drawing как None

    def at(self, start_x, start_y):
        self.start = (start_x, start_y)
        return self

    def to(self, end_x, end_y=None):
        self.end = (end_x, end_y)
        return self

    def arrow(self, size=None, pos=0.54, color='black', reverse=False,
              filled=True, zorder=3, head_length=0.6,
              head_width=0.2):
        self.arrow_params = {
            'size': size,
            'pos': pos,
            'color': color,
            'reverse': reverse,
            'filled': filled,
            'zorder': zorder,
            'head_length': head_length,
            'head_width': head_width
        }
        if size is not None:
            self.arrow_params['size'] = size
        return self


    def _add_arrow(self, ax, x_values, y_values):
        x_values, y_values = interpolate_curve(x_values, y_values)
        if self.arrow_params:
            index = int(len(x_values) * self.arrow_params['pos'])
            x, y = x_values[index], y_values[index]
            arrow_size = self.arrow_params.get('size')
            if arrow_size is None:
                arrow_size = self.config.get('arrow_size', 27)

            # Вычисляем угол наклона стрелки
            if index < len(x_values) - 1:
                dx = x_values[index + 1] - x
                dy = y_values[index + 1] - y
            else:
                dx = x - x_values[index - 1]
                dy = y - y_values[index - 1]

            # Разворачиваем стрелку, если требуется
            if self.arrow_params['reverse']:
                dx, dy = -dx, -dy

            # Определяем стиль стрелки
            if self.arrow_params['filled']:
                style = ArrowStyle('-|>', head_length=self.arrow_params['head_length'],
                                   head_width=self.arrow_params['head_width'])
            else:
                style = ArrowStyle('->', head_length=self.arrow_params['head_length'],
                                   head_width=self.arrow_params['head_width'])

            # Создаем и добавляем стрелку на график
            arrow = FancyArrowPatch(
                (x, y), (x + dx, y + dy),
                arrowstyle=style,
                color=self.arrow_params['color'],
                mutation_scale=arrow_size,
                zorder=self.arrow_params['zorder']
            )
            ax.add_patch(arrow)


    def col(self, color):
        self.color = color
        return self

    def ls(self, linestyle):
        self.linestyle = linestyle
        return self

    def lw(self, linewidth):
        self.linewidth = linewidth
        return self
    
    def dot(self, pos='end', **kwargs):
        default_params = {'size': 8, 'color': 'black'}  # Значения по умолчанию
        dot_params = {**default_params, **kwargs}  # Объединение значений по умолчанию с пользовательскими параметрами

        if pos in ['start', 'end', 'both']:
            if pos == 'both':
                self.dots_params['start'] = self.dots_params['end'] = dot_params
            else:
                self.dots_params[pos] = dot_params
        return self

    def _add_dots(self, ax):
        for position in ['start', 'end']:
            if self.dots_params[position]:
                point = self.start if position == 'start' else self.end
                # Убедимся, что точка содержит обе координаты
                if point and None not in point:
                    ax.plot(point[0], point[1], marker='o', 
                            markersize=self.dots_params[position].get('size', 6),
                            color=self.dots_params[position].get('color', 'k'))

    def calculate_ofst(self, point=None):
        # Убедимся, что конфигурация доступна
        if not hasattr(self, 'config') or not self.config:
            raise ValueError("Config not set for this process.")

        # Используем конфигурацию напрямую из self.config
        xlen = self.config['xlim'][1] - self.config['xlim'][0]
        ylen = self.config['ylim'][1] - self.config['ylim'][0]

        if self.config['center']:
            center_x, center_y = self.config['center']
        else:
            center_x = self.config['center_x'] if self.config['center_x'] else xlen/2
            center_y = self.config['center_y'] if self.config['center_y'] else ylen/2
        
        # Вычисляем смещение в зависимости от положения точки
        k = self.config['fontsize'] / 27
        dx = xlen * 0.05 * k if point and point[0] >= center_x else -xlen * 0.05 * k
        dy = ylen * 0.06 * k if point and point[1] >= center_y else -ylen * 0.05 * k

        return (dx, dy)

    def label(self, text1=None, text2=None, ofst=None, start_ofst=None, end_ofst=None, 
              end_dx=None, end_dy=None, start_dx=None, start_dy=None):
        if start_ofst is None and (start_dx is not None or start_dy is not None):
            start_ofst = (start_dx, start_dy)

        if end_ofst is None and (end_dx is not None or end_dy is not None):
            end_ofst = (end_dx, end_dy)

        if isinstance(self, State):
            # Для State применяем метку и смещение к единственной точке
            self.start_label = {'text': text1, 'ofst': start_ofst}
        else:
            if text2 is None:
                # Если задан только один текст, применяем метку к начальной точке
                self.start_label = {'text': text1, 'ofst': start_ofst}
            else:
                # Если заданы обе метки, применяем их к начальной и конечной точкам
                self.start_label = {'text': text1, 'ofst': start_ofst}
                self.end_label = {'text': text2, 'ofst': end_ofst}
        return self


    def _add_labels(self, ax, config):
        def add_label(point, label_data, ax, config):
            if label_data['ofst'] is None:
                dx, dy = self.calculate_ofst(point)
            else:
                dx, dy = label_data['ofst']
                # Если dx или dy не заданы, используем значения по умолчанию
                if dx is None or dy is None:
                    default_dx, default_dy = self.calculate_ofst(point)
                    dx = dx if dx is not None else default_dx
                    dy = dy if dy is not None else default_dy

            ax.text(point[0] + dx, point[1] + dy, label_data['text'],
                    fontsize=config['fontsize'], ha='center', va='center')


        if hasattr(self, 'start_label') and self.start:
            add_label(self.start, self.start_label, ax, config)

        if hasattr(self, 'end_label') and self.end:
            add_label(self.end, self.end_label, ax, config)


    # Для работы Bezier().connect()
    def tangent_at_end(self):
        if hasattr(self, 'x_values') and hasattr(self, 'y_values') and len(self.x_values) > 1:
            # Используем последние две точки для определения касательной
            direction = (self.x_values[-1] - self.x_values[-2], self.y_values[-1] - self.y_values[-2])
            return direction
        return None

    def tangent_at_start(self):
        if hasattr(self, 'x_values') and hasattr(self, 'y_values') and len(self.x_values) > 1:
            # Используем первые две точки для определения касательной
            direction = (self.x_values[1] - self.x_values[0], self.y_values[1] - self.y_values[0])
            return direction
        return None
        

    def tox(self, type='both', color='k', ls='--', lw=1.6):
        self.extra_lines.append(('x', type, color, ls, lw))
        return self

    def toy(self, type='both', color='k', ls='--', lw=1.6):
        self.extra_lines.append(('y', type, color, ls, lw))
        return self

    def tozero(self, type='both', color='k', ls='--', lw=1.6):
        self.extra_lines.append(('zero', type, color, ls, lw))
        return self

    def xtick(self, *labels, which=None):
        # Функция для преобразования числа в строку с заменой точки на запятую
        def format_label(value):
            return f'${str(value).replace(".", "{,}")}$'
        # Если метки не заданы, используем числовые значения координат
        if not labels:
            if isinstance(self, State) or which == 'start':
                self.start_xtick_label = format_label(self.start[0])
            elif which == 'end' and self.end is not None:
                self.end_xtick_label = format_label(self.end[0])
            elif self.end is not None:
                # Добавляем метки для обеих точек
                self.start_xtick_label = format_label(self.start[0])
                self.end_xtick_label = format_label(self.end[0])
        else:
            if len(labels) == 1:
                if which == 'end':
                    self.end_xtick_label = labels[0]
                else:
                    self.start_xtick_label = labels[0]
            elif len(labels) == 2:
                self.start_xtick_label, self.end_xtick_label = labels

        return self

    def ytick(self, *labels, which=None):
        # Функция для преобразования числа в строку с заменой точки на запятую
        def format_label(value):
            return f'${str(value).replace(".", "{,}")}$'
        # Если метки не заданы, используем числовые значения координат
        if not labels:
            if isinstance(self, State) or which == 'start':
                self.start_ytick_label = format_label(self.start[1])
            elif which == 'end' and self.end is not None:
                self.end_ytick_label = format_label(self.end[1])
            elif self.end is not None:
                # Добавляем метки для обеих точек
                self.start_ytick_label = format_label(self.start[1])
                self.end_ytick_label = format_label(self.end[1])
        else:
            if len(labels) == 1:
                if which == 'end':
                    self.end_ytick_label = labels[0]
                else:
                    self.start_ytick_label = labels[0]
            elif len(labels) == 2:
                self.start_ytick_label, self.end_ytick_label = labels

        return self

    def plot(self, ax, config):
        if hasattr(self, 'x_values') and hasattr(self, 'y_values'):
            ax.plot(self.x_values, self.y_values, color=self.color,
                    linestyle=self.linestyle, linewidth=self.linewidth)
            if self.arrow_params:
                self._add_arrow(ax, self.x_values, self.y_values)
            self._add_dots(ax)
        # Добавляем подписи около точек
        self._add_labels(ax, config)

class State(Process):
    def __init__(self, drawing=None):
        super().__init__()  # Вызываем конструктор базового класса
        self.draw_dot = False  # Флаг для управления отрисовкой точки
        self.type = 'state'
        self.dot_params = {'size': 6, 'color': 'black'}  # Значения по умолчанию для точки
        self.label_text = ''
        self.label_ofst = None
        if drawing:
            self.ax = drawing.ax
            self.config = drawing.config
        else:
            self.ax = None
            self.config = {}

    def at(self, x, y):
        self.start = (x, y)  # У State только начальная точка (как и конечная)
        return self

    def dot(self, size=6, color='k'):
        self.dot_params = {'size': size, 'color': color}
        self.draw_dot = True
        return self

    def plot(self, ax, config):
        if self.start is None:
            raise ValueError("Start point not set for State.")

        x, y = self.start

        # Рисование точки
        if self.draw_dot:
            ax.plot(x, y, 'o', markersize=self.dot_params['size'], color=self.dot_params['color'])

        ## Если задана подпись, рисуем ее
        self._add_labels(ax, config)
            
        return self

class Linear(Process):
    def __init__(self):
        super().__init__()
        self.type = 'linear'
    def plot(self, ax, config):
        if self.start and self.end:
            V1, p1 = self.start
            V2, p2 = self.end
            self.x_values = np.linspace(V1, V2, 100)
            self.y_values = np.linspace(p1, p2, 100)
            super().plot(ax, config)

class Iso_t(Process):
    def __init__(self):
        super().__init__()
        self.type = 'iso_t'

    def plot(self, ax, config):
        if self.start is None:
            if self.drawing and self.drawing.last_point:
                self.start = self.drawing.last_point
            else:
                raise ValueError("Start point must be set for 'Iso_t' process.")

        V1, p1 = self.start

        # Если конечная точка не определена, используем параметры из метода to()
        if self.end is None:
            raise ValueError("End point must be set for 'Iso_t' process.")

        # Убедимся, что end_y_or_type было задано
        if isinstance(self.end, tuple) and isinstance(self.end[1], str):
            end_x, end_y_or_type = self.end
            if end_y_or_type == 'volume':
                V2 = end_x
                p2 = p1 * V1 / V2
            elif end_y_or_type == 'pressure':
                p2 = end_x
                V2 = p1 * V1 / p2
            self.end = (V2, p2)

        V2, p2 = self.end

        self.x_values = np.linspace(V1, V2, 100)
        self.y_values = p1 * V1 / self.x_values
        #self.config = config  # Сохранение config в объекте
        super().plot(ax, config)

    def to(self, end_x, end_y_or_type=None):
        self.end = (end_x, end_y_or_type)
        return self

class Power(Process):
    def __init__(self, power=2, drawing=None):
        super().__init__()
        self.type = 'power'
        self.power = power
        #self.drawing = drawing  # Сохраняем контекст рисования

    def plot(self, ax, config):
        # Если начальная точка не задана, используем последнюю точку из контекста рисования
        if self.start is None and self.drawing and self.drawing.last_point:
            self.start = self.drawing.last_point

        # Если конечная точка не задана, используем параметры из метода to()
        if self.end is None:
            raise ValueError("End point must be set for 'Power' process.")

        x1, y1 = self.start

        # Убедимся, что end_y_or_type было задано
        if isinstance(self.end, tuple) and isinstance(self.end[1], str):
            end_x, end_y_or_type = self.end
            if end_y_or_type == 'x':
                x2 = end_x
                y2 = y1 * (x2 / x1) ** self.power
            elif end_y_or_type == 'y':
                y2 = end_x
                x2 = (y2 / y1) ** (1 / self.power) * x1
            self.end = (x2, y2)

        x2, y2 = self.end

        # y = kx^n + b
        # Решение системы уравнений для нахождения k и b
        k = (y2 - y1) / (x2**self.power - x1**self.power)
        b = y1 - k * x1**self.power
        self.x_values = np.linspace(x1, x2, 100)
        self.y_values = k * self.x_values**self.power + b

        super().plot(ax, config)

    def to(self, end_x, end_y_or_type=None):
        self.end = (end_x, end_y_or_type)
        return self

class Adiabatic(Process):
    def __init__(self, gamma=5/3):
        super().__init__()
        self.gamma = gamma
        self.type = 'adiabatic'

    def plot(self, ax, config):
        if self.start is None:
            if self.drawing and self.drawing.last_point:
                self.start = self.drawing.last_point
            else:
                raise ValueError("Start point must be set for 'Adiabatic' process.")

        V1, p1 = self.start

        # Если конечная точка не определена, используем параметры из метода to()
        if self.end is None:
            raise ValueError("End point must be set for 'Adiabatic' process.")

        # Убедимся, что end_y_or_type было задано
        if isinstance(self.end, tuple) and isinstance(self.end[1], str):
            end_x, end_y_or_type = self.end
            if end_y_or_type == 'volume':
                V2 = end_x
                p2 = (p1 * V1 ** self.gamma) / V2 ** self.gamma
            elif end_y_or_type == 'pressure':
                p2 = end_x
                V2 = (p1 * V1 ** self.gamma / p2) ** (1 / self.gamma)
            self.end = (V2, p2)

        V2, p2 = self.end

        self.x_values = np.linspace(V1, V2, 100)
        self.y_values = (p1 * V1 ** self.gamma) / self.x_values ** self.gamma
        super().plot(ax, config)

    def to(self, end_x, end_y_or_type=None):
        self.end = (end_x, end_y_or_type)
        return self

class Bezier(Process):
    def __init__(self, x=0, y=0, x1=None, y1=None, x2=None, y2=None):
        super().__init__()
        self.type = 'bezier'
        self.x = x
        self.y = y
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.coordinates = []  # Список для хранения координат кривой

    def connect(self, process1, process2):
        # Находим точку пересечения процессов
        intersection_point = self._find_intersection(process1, process2)

        # Устанавливаем начальную и конечную точки, а также контрольную точку
        self.start = process1.end if process1.end else process1.start
        self.end = process2.start if process2.start else process2.end
        self.x = intersection_point[0]
        self.y = intersection_point[1]

        return self

    def _find_intersection(self, process1, process2):
        tangent1 = process1.tangent_at_end()
        tangent2 = process2.tangent_at_start()

        if tangent1 is None or tangent2 is None:
            return None  # Невозможно вычислить точку пересечения

        x1, y1 = process1.end
        x2, y2 = x1 + tangent1[0], y1 + tangent1[1]
        x3, y3 = process2.start
        x4, y4 = x3 + tangent2[0], y3 + tangent2[1]

        # Вычисление угловых коэффициентов (наклонов)
        k1 = (y2 - y1) / (x2 - x1)
        k2 = (y4 - y3) / (x4 - x3)

        # Вычисление точек пересечения с осью Y
        b1 = y1 - k1 * x1
        b2 = y3 - k2 * x3

        # Проверка на параллельность
        if k1 == k2:
            # Процессы параллельны, нужно выбрать другой способ соединения
            return None

        # Находим точку пересечения
        intersection_x = (b2 - b1) / (k1 - k2)
        intersection_y = k1 * intersection_x + b1

        return intersection_x, intersection_y

    def plot(self, ax, config):
        if self.start and self.end: # зачем эта проверка? Что происходит else?
            x1, y1 = self.start
            x2, y2 = self.end
            t = np.linspace(0, 1, 100)

            if self.x1 is not None and self.x2 is not None:
                # Кривая Безье третьего порядка
                self.x_values = (1-t)**3 * x1 + 3 * (1-t)**2 * t * self.x1 + 3 * (1-t) * t**2 * self.x2 + t**3 * x2
                self.y_values = (1-t)**3 * y1 + 3 * (1-t)**2 * t * self.y1 + 3 * (1-t) * t**2 * self.y2 + t**3 * y2
            else:
                # Кривая Безье второго порядка
                self.x_values = (1-t)**2 * x1 + 2 * (1-t) * t * self.x + t**2 * x2
                self.y_values = (1-t)**2 * y1 + 2 * (1-t) * t * self.y + t**2 * y2

            self.coordinates = list(zip(self.x_values, self.y_values))
            super().plot(ax, config)


    def get_point(self, n):
        if 0 <= n < len(self.coordinates):
            return self.coordinates[n][0], self.coordinates[n][1]
        else:
            raise IndexError("Индекс за пределами диапазона точек кривой Безье.")


    def get_coordinates(self):
        if self.coordinates:
            # Разбиваем список кортежей на два списка для координат x и y
            x_values, y_values = zip(*self.coordinates)
            return x_values, y_values
        else:
            return [], []  # Возвращаем пустые списки, если координат нет


    def to(self, end_x, end_y=None):
        self.end = (end_x, end_y)
        return self



def end_x(process):
    if process.type == 'power':
        x1, y1 = process.start
        _, y2 = process.end
        return x1 * (y2 / y1)**0.5

def end_y(process):
    if process.type == 'power':
        x1, y1 = process.start
        x2, _ = process.end
        return y1 * (x2 / x1)**2

def end_v(process):
    V1, p1 = process.start
    if process.type == 'iso_t':
        _, p2 = process.end
        return V1 * p1 / p2
    elif process.type == 'adiabatic':
        _, p2 = process.end
        return V1 * (p1 / p2) ** (1 / process.gamma)
    return None

def end_p(process):
    V1, p1 = process.start
    if process.type == 'iso_t':
        V2, _ = process.end
        return p1 * V1 / V2
    elif process.type == 'adiabatic':
        V2, _ = process.end
        return (p1 * V1 ** process.gamma) / V2 ** process.gamma
    return None

def common_pv(v1, p1, v3, p3, gamma=5/3):
    v2 = v1**(gamma/(gamma-1)) * (p1 / (p3 * v3))**(1/(gamma-1))
    p2 = p3*v3/v2
    return v2,p2

# Find intersection adiabatic and iso_t
def common_QT(process1, process2, gamma=5/3):
    if process1.type == 'state':
        x1, y1 = process1.start
    else:
        x1, y1 = process1.end
    if process2.type == 'state':
        x2, y2 = process2.start
    else:
        x2, y2 = process2.end
    ### Calculate common x, y
    x = (y1*x1**gamma / (y2*x2))**(1/(gamma-1))
    y = y2*x2/x
    return x,y 

def interpolate_curve(x_values, y_values, num_points=100):
    # Вычисляем длину кривой
    total_length = np.sum(np.sqrt(np.diff(x_values)**2 + np.diff(y_values)**2))
    length_along_curve = np.insert(np.cumsum(np.sqrt(np.diff(x_values)**2 + np.diff(y_values)**2)), 0, 0)

    # Ограничиваем максимальное расстояние максимальным значением длины кривой
    max_length = length_along_curve[-1]
    distance = np.linspace(0, max_length, num_points)

    # Интерполируем x и y как функции от длины
    f_x = interp1d(length_along_curve, x_values, kind='linear', bounds_error=False, fill_value="extrapolate")
    f_y = interp1d(length_along_curve, y_values, kind='linear', bounds_error=False, fill_value="extrapolate")

    # Вычисляем новые значения x и y
    new_x_values = f_x(distance)
    new_y_values = f_y(distance)

    return new_x_values, new_y_values
