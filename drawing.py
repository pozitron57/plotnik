import os
import matplotlib.pyplot as plt
from matplotlib import rcParams
from matplotlib.patches import FancyArrowPatch
import numpy as np
from .processes import Process

class Drawing:
    def __init__(self):
        self.last_point = None
        self.config = {'font': 'stix',
                       'fontsize': 34,
                       'lw': 3.2,
                       'aspect': 1,
                       'xlim': [0, 10.7],
                       'ylim': [0, 10.7],
                       'xname': '',
                       'yname': '',
                       'yname_y': None,
                       'xname_x': None,
                       'xname_ofst': None,
                       'yname_ofst': None,
                       'zero': True,
                       'zero_x': 0,
                       'zero_ofst': None,
                       'axes_arrow_width': None,  # стрелки осей
                       'axes_arrow_length': None, # стрелки осей
                       'axes_arrow_scale': 1,     # стрелки осей
                       'arrow_size': 27,          # стрелки процессов
                       'tick_width': None,
                       'tick_length': None,
                       'center_x': None,
                       'center_y': None,
                       'center': None,
                       }
        self.grid_config = {}  # Инициализация grid_config как пустого словаря
        self.fig = None
        self.ax = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        plt.close(self.fig)

    def __iadd__(self, process):
        self.add_process(process)
        return self

    def update_rcParams(self):
        tick_length = self.config['tick_length'] if self.config['tick_length'] is not None else 6.5
        tick_width = self.config['tick_width'] if self.config['tick_width'] is not None else 2
        plt.rcParams.update({
            "font.size": self.config['fontsize'],
            "xtick.major.size": tick_length,
            "ytick.major.size": tick_length,
            "xtick.major.width": tick_width,
            "ytick.major.width": tick_width,
        })
        if 'stix' in self.config.get('font', ''):
            plt.rcParams.update({
                "text.usetex": False,
                "mathtext.fontset": "custom",
                "mathtext.it": "STIX Two Text:italic",
                "mathtext.rm": "STIX Two Text",
                "mathtext.sf": "STIX Two Text",
                "font.sans-serif": "STIX Two Text",
            })
        else:
            plt.rcParams.update({
                "text.usetex": True,
                "font.family": "serif",
                "text.latex.preamble": "\n".join([
                    r"\usepackage[T2A]{fontenc}",
                    r"\usepackage[utf8]{inputenc}",
                    r"\usepackage[russian]{babel}"
                ])
            })

        # Создаем фигуру и оси
        self.fig, self.ax = plt.subplots()

        # Скрываем стандартные линии осей
        self.ax.spines['top'].set_visible(False)
        self.ax.spines['right'].set_visible(False)
        self.ax.spines['bottom'].set_visible(False)
        self.ax.spines['left'].set_visible(False)
        self.ax.spines['bottom'].set_position('zero')
        self.ax.spines['left'].set_position('zero')

        # Отключение подписей значений осей
        self.ax.set_xticks([])
        self.ax.set_yticks([])
        
    def set_config(self, **kwargs):
        self.config.update(kwargs)
        self.update_rcParams()  # Обновление plt.rcParams с новыми настройками конфига
        
        # Устанавливаем границы осей, если они заданы
        if 'xlim' in kwargs:
            self.ax.set_xlim(kwargs['xlim'])
        if 'ylim' in kwargs:
            self.ax.set_ylim(kwargs['ylim'])
        #xlim = self.config.get('xlim', self.ax.get_xlim())
        #ylim = self.config.get('ylim', self.ax.get_ylim())

    def add_process(self, process):
        #process.drawing = self  # Устанавливаем контекст рисования для процесса
        process.config = self.config  # Устанавливаем config для процесса
        if process.start is None and self.last_point is not None:
            process.at(*self.last_point)  # Установка начальной точки, если не задана

        process.plot(self.ax, self.config)  # Отрисовка процесса

        if hasattr(process, 'start_ytick_label'):
            self._add_ytick_label(process.start[1], process.start_ytick_label)
        if hasattr(process, 'end_ytick_label'):
            self._add_ytick_label(process.end[1], process.end_ytick_label)
        if hasattr(process, 'start_xtick_label'):
            self._add_xtick_label(process.start[0], process.start_xtick_label)
        if hasattr(process, 'end_xtick_label'):
            self._add_xtick_label(process.end[0], process.end_xtick_label)
        
        # Отрисовка дополнительных линий (tox, toy, tozero)
        for line_type, line_part, color, ls, lw in process.extra_lines:
            start_x, start_y = process.start if process.start else (None, None)
            end_x, end_y = process.end if process.end else (None, None)

            if line_type == 'x':
                if line_part in ['both', 'start'] and start_x is not None:
                    self.ax.plot([start_x, start_x], [start_y, 0], color=color, linestyle=ls, linewidth=lw)
                if line_part in ['both', 'end'] and end_x is not None:
                    self.ax.plot([end_x, end_x], [end_y, 0], color=color, linestyle=ls, linewidth=lw)
            elif line_type == 'y':
                # Аналогично для 'y'
                if line_part in ['both', 'start'] and start_y is not None:
                    self.ax.plot([start_x, 0], [start_y, start_y], color=color, linestyle=ls, linewidth=lw)
                if line_part in ['both', 'end'] and end_y is not None:
                    self.ax.plot([end_x, 0], [end_y, end_y], color=color, linestyle=ls, linewidth=lw)
            elif line_type == 'zero':
                # Аналогично для 'zero'
                if line_part in ['both', 'start'] and start_x is not None and start_y is not None:
                    self.ax.plot([0, start_x], [0, start_y], color=color, linestyle=ls, linewidth=lw)
                if line_part in ['both', 'end'] and end_x is not None and end_y is not None:
                    self.ax.plot([0, end_x], [0, end_y], color=color, linestyle=ls, linewidth=lw)

        if process.end is not None:
            self.last_point = process.end  # Обновление последней точки для следующего процесса

    def grid(self, step=None, step_x=None, step_y=None, ls='-', color='#777777', lw=0.9, zorder=-9, Nx=None, Ny=None, x_start=None, x_end=None, y_start=None, y_end=None):
        # Игнорирование step_x и step_y, если step задан
        if step is not None:
            if step_x is not None or step_y is not None:
                print("Warning: 'step_x' and 'step_y' are ignored because 'step' is set.")
            step_x = step_y = step

        # Установка стандартных значений для step_x и step_y, если они не заданы
        default_step = 1
        if step_x is None:
            step_x = default_step
        if step_y is None:
            step_y = default_step
        if Nx is not None:
            self.grid_config['Nx'] = Nx
        if Ny is not None:
            self.grid_config['Ny'] = Ny
        if x_start is not None:
            self.grid_config['x_start'] = x_start
        if x_end is not None:
            self.grid_config['x_end'] = x_end
        if y_start is not None:
            self.grid_config['y_start'] = y_start
        if y_end is not None:
            self.grid_config['y_end'] = y_end
        if step is not None:
            self.grid_config['step_x'] = self.grid_config['step_y'] = step
        if step_x is not None:
            self.grid_config['step_x'] = step_x
        if step_y is not None:
            self.grid_config['step_y'] = step_y

        self.grid_config.update({'ls': ls, 'color': color, 'lw': lw, 'zorder': zorder})
        self.config['grid'] = True

    def _add_grid(self):
        xlim = self.config.get('xlim', self.ax.get_xlim())
        ylim = self.config.get('ylim', self.ax.get_ylim())

        grid_config = self.grid_config
        Nx = grid_config.get('Nx', int((xlim[1] - xlim[0]) // grid_config.get('step_x', 5)) - 1)
        Ny = grid_config.get('Ny', int((ylim[1] - ylim[0]) // grid_config.get('step_y', 5)))

        # Рассчитываем диапазон и шаги для сетки
        x_step = grid_config['step_x']
        y_step = grid_config['step_y']

        x_start = grid_config.get('x_start', max(xlim[0], 0 - (Nx // 2) * x_step) )
        x_end = grid_config.get('x_end', min(xlim[1], x_start + Nx * x_step) )
        if ylim[0] >= 0:
            y_start = grid_config.get('y_start', y_step * (ylim[0] // y_step) )
        else:
            y_start = grid_config.get('y_start', y_step * (ylim[0] // y_step+1) )
        y_end = grid_config.get('y_end', min(ylim[1], y_start + Ny * y_step) )

        # Рисуем вертикальные линии сетки
        for x in np.arange(x_start, x_end + grid_config['step_x'], grid_config['step_x']):
            if x != 0 and xlim[0] <= x <= min(xlim[1], x_end):  # Учитываем x_end и игнорируем линию, совпадающую с осью Y
                self.ax.plot([x, x], [y_start, y_end], linestyle=grid_config['ls'], 
                             color=grid_config['color'], linewidth=grid_config['lw'], 
                             zorder=grid_config['zorder'], clip_on=False)

        # Рисуем горизонтальные линии сетки
        for y in np.arange(y_start, y_end + y_step, y_step):
            if y != 0 and ylim[0] <= y <= min(ylim[1], y_end):  # Учитываем y_end и игнорируем линию, совпадающую с осью X
                self.ax.plot([x_start, x_end], [y, y], linestyle=grid_config['ls'], 
                             color=grid_config['color'], linewidth=grid_config['lw'], 
                             zorder=grid_config['zorder'], clip_on=False)

    def _add_xtick_label(self, x, label):
        xlen = self.config['xlim'][1] - self.config['xlim'][0]
        ylen = self.config['ylim'][1] - self.config['ylim'][0]
        xlabel_ofst = self.config.get('xlabel_ofst', [xlen * 0.02, ylen * 0.14 * self.config['fontsize']/30])
        if self.config['tick_length'] is not None:
            tick_length = self.config['tick_length']
        else: 
            tick_length = xlabel_ofst[1]*0.2
        # Рисование текста метки
        self.ax.text(x, -xlabel_ofst[1], label, va='baseline', ha='center', fontsize=self.config['fontsize'])
        # Рисование штриха
        self.ax.plot([x, x], [0, -tick_length], color='k',
                     linestyle='-', linewidth=self.config['lw'] * 0.8,
                     clip_on=False)

    def _add_ytick_label(self, y_val, label):
        xlen = self.config['xlim'][1] - self.config['xlim'][0]
        ylen = self.config['ylim'][1] - self.config['ylim'][0]
        aspect = self.config['aspect']

        ylabel_ofst = self.config.get('ylabel_ofst', [xlen * 0.05 * aspect, ylen * 0.03])
        xlabel_ofst = self.config.get('xlabel_ofst', [xlen * 0.02, ylen * 0.14 * self.config['fontsize']/30])
        if self.config['tick_length'] is not None:
            tick_length = self.config['tick_length']
        else: 
            tick_length = xlabel_ofst[1]*0.2 * aspect

        # Рисование текста метки
        self.ax.text(-ylabel_ofst[0], y_val, label, va='center', ha='right', fontsize=self.config['fontsize'])
        # Рисование штриха
        self.ax.plot([-tick_length, 0], [y_val, y_val], color='k',
                     linestyle='-', linewidth=self.config['lw'] * 0.8,
                     clip_on=False)
            
    def add_xticks(self, xticks, names=None, bg=False, bgcolor='white', bgsize=None, direction='out'):
        ylen = self.config['ylim'][1] - self.config['ylim'][0]
        xlen = self.config['xlim'][1] - self.config['xlim'][0]
        xlabel_ofst = self.config.get('xlabel_ofst', [xlen * 0.02, ylen * 0.14 * self.config['fontsize']/30])

        if self.config['tick_length'] is None:
            tick_length = xlabel_ofst[1]*0.2
        else:
            tick_length = self.config['tick_length']

        # Преобразование списка значений в словарь для замены названий
        if names is not None and len(names) == len(xticks):
            label_dict = dict(zip(xticks, names))
        else:
            label_dict = {}

        for x in xticks:
            # Заменяем значение на соответствующее имя, если оно есть в словаре
            x_label = label_dict.get(x, x)
            # Если метка является числом, заменяем точку на запятую
            if isinstance(x, (int, float)):
                x_label = f"{x_label}".replace('.', ',')
            # Оборачиваем метку в LaTeX
            #x_label = f"${x_label}$"

            if bg:
                # Настройка фона подписи
                bg_params = {'boxstyle': 'round,pad=0.1', 'facecolor': bgcolor, 'edgecolor': 'none', 'alpha': 1}
                if bgsize:
                    bg_params['boxstyle'] = f'round,pad={bgsize}'
                # Добавление текста с фоном
                self.ax.text(x, -xlabel_ofst[1], x_label, va='baseline', ha='center', 
                             fontsize=self.config['fontsize'], bbox=bg_params)
            else:
                # Добавление текста без фона
                self.ax.text(x, -xlabel_ofst[1], x_label, va='baseline', ha='center', 
                             fontsize=self.config['fontsize'])

            # Рисование штриха
            if direction == 'out':
                end = -tick_length
            elif direction == 'in':
                end = tick_length
            else:
                end = 0

            self.ax.plot([x, x], [0, end], color='k', linestyle='-', 
                         linewidth=self.config['lw'] * 0.8, clip_on=False)


    def add_yticks(self, yticks, names=None, direction='out'):
        aspect = self.config['aspect']
        xlen = self.config['xlim'][1] - self.config['xlim'][0]
        ylen = self.config['ylim'][1] - self.config['ylim'][0]
        ylabel_ofst = self.config.get('ylabel_ofst', [xlen * 0.05 * aspect, ylen * 0.03])
        xlabel_ofst = self.config.get('xlabel_ofst', [xlen * 0.02, ylen * 0.14 * self.config['fontsize']/30])

        if self.config['tick_length'] is None:
            tick_length = xlabel_ofst[1]*0.2
        else:
            tick_length = self.config['tick_length']

        # Преобразование списка значений в словарь для замены названий
        if names is not None and len(names) == len(yticks):
            label_dict = dict(zip(yticks, names))
        else:
            label_dict = {}

        for y in yticks:
            # Заменяем значение на соответствующее имя, если оно есть в словаре
            y_label = label_dict.get(y, y)
            # Если метка является числом, заменяем точку на запятую
            if isinstance(y, (int, float)):
                y_label = f"{y_label}".replace('.', ',')
            y_label = f"${y_label}$"
            self.ax.text(-ylabel_ofst[0], y, y_label, va='center', ha='right',
                         fontsize=self.config['fontsize'])

            # Рисование штриха
            if direction == 'out':
                start = -tick_length*aspect
            elif direction == 'in':
                start = tick_length*aspect
            else:
                start = 0

            self.ax.plot([start, 0], [y, y], 'k-', clip_on=False, linewidth=self.config['lw'] * 0.8)


    def show(self):
        xlen = self.config['xlim'][1] - self.config['xlim'][0]
        ylen = self.config['ylim'][1] - self.config['ylim'][0]
        lw = self.config['lw']*0.8

        xlim = self.config.get('xlim', self.ax.get_xlim())
        ylim = self.config.get('ylim', self.ax.get_ylim())

        # Установка аспекта, если он задан
        if 'aspect' in self.config:
            self.ax.set_aspect(self.config['aspect'])
            aspect = self.config['aspect']
        else:
            aspect = 1

        # Координатные оси
        longer_axis = np.amax([xlen,ylen])
        k = 1/2
        axes_arrow_width = self.config.get('axes_arrow_width')
        axes_arrow_length = self.config.get('axes_arrow_length')
        if ylen >= xlen:
            if axes_arrow_width is None:
                hw_x = longer_axis * 0.03
                hw_y = longer_axis * 0.03 * aspect
            else:
                hw_x = axes_arrow_width
                hw_y = axes_arrow_width * aspect
            if axes_arrow_length is None:
                hl_x = longer_axis * 0.08 * aspect
                hl_y = longer_axis * 0.08
            else:
                hl_x = axes_arrow_length * aspect
                hl_y = axes_arrow_length

        else:
            if axes_arrow_width is None:
                hw_x = longer_axis * 0.03 / aspect * k
                hw_y = longer_axis * 0.03 * k
            else:
                hw_x = axes_arrow_width / aspect * k
                hw_y = axes_arrow_width * k
            if axes_arrow_length is None:
                hl_x = longer_axis * 0.08 * k
                hl_y = longer_axis * 0.08 / aspect * k
            else:
                hl_x = axes_arrow_length * k
                hl_y = axes_arrow_length / aspect * k

        axes_arrow_scale = self.config.get('axes_arrow_scale', 1)

        # Создание стрелки для оси X с закругленным концом
        arrowstyle_x = f"-|>,head_length={hl_x},head_width={hw_x}"
        arrow_x = FancyArrowPatch((xlim[0], 0), (xlim[1], 0),
                                  clip_on=False,
                                  arrowstyle=arrowstyle_x,
                                  mutation_scale= 200 / xlen * axes_arrow_scale,
                                  mutation_aspect=aspect,
                                  shrinkA=0,
                                  shrinkB=0,
                                  lw=lw, color='k', zorder=5)
        self.ax.add_patch(arrow_x)
        # Создание стрелки для оси Y с закругленным концом и корректировкой длины
        arrowstyle_y = f"-|>,head_length={hl_y},head_width={hw_y}"
        arrow_y = FancyArrowPatch((0, ylim[0]), (0, ylim[1]),
                                  clip_on=False,
                                  arrowstyle=arrowstyle_y,
                                  mutation_scale= 200 / xlen * axes_arrow_scale,
                                  mutation_aspect=aspect,
                                  shrinkA=0,
                                  shrinkB=0,
                                  lw=lw, color='k', zorder=5)
        self.ax.add_patch(arrow_y)


        # Получаем настройки смещения подписей осей
        xlabel_ofst = self.config.get('xlabel_ofst', [xlen * 0.02, ylen * 0.14 * self.config['fontsize']/30])
        ylabel_ofst = self.config.get('ylabel_ofst', [xlen * 0.05 * aspect, ylen * 0.03])

        # Добавляем подписи осей xname, yname
        # Если xname_ofst, yname_ofst не заданы,
        # то yname по вертикали выровнен с ylabels, а
        # xname выровнен по горизонтали с xlabels
        if self.config['xname_ofst'] is None:
            x_dx =  xlabel_ofst[0]
            x_dy = -xlabel_ofst[1]
        else:
            x_dx =  self.config['xname_ofst'][0]
            x_dy =  self.config['xname_ofst'][1]

        # Если yname задан в set_config, добавить новым тиком и удалить штрих
        # Если yname_y задан в set_config, добавить новым тиком на координату y и удалить штрих
        # Если yname_ofst задан в set_config, то yname добавляется не штрихом, а через
        # ax.text()
        if self.config['yname'] is not None:
            # Если yname_ofst задан в set_config, то yname добавляется через ax.text()
            if self.config['yname_ofst'] is not None:
                arrow_tip_y = ylim[1] - hl_y
                # Отступ для yname, отсчитываемый от конца стрелки
                yname_offset_x, yname_offset_y = self.config['yname_ofst']
                # Новое положение yname
                new_yname_pos_x = -yname_offset_x
                new_yname_pos_y = arrow_tip_y + yname_offset_y
                self.ax.text(new_yname_pos_x, new_yname_pos_y,
                             self.config['yname'], ha='right', va='top',
                             fontsize=self.config['fontsize'])
            else:
                current_ticks = list(self.ax.get_yticks())
                current_labels = [tick.get_text() for tick in self.ax.get_yticklabels()]

                # Определение положения для нового тика
                if self.config['yname_y'] is not None:
                    new_tick = self.config['yname_y']
                #elif current_ticks:
                    #new_tick = max(current_ticks) + (current_ticks[1] - current_ticks[0] if len(current_ticks) > 1 else 1)
                else:
                    new_tick = ylim[1]

                # Добавляем yname как новый тик
                if new_tick not in current_ticks:
                    current_ticks.append(new_tick)
                    current_labels.append(self.config['yname'])

                    self.ax.set_yticks(current_ticks)
                    self.ax.set_yticklabels(current_labels)

                    # Удаляем штрих у новой метки
                    ticks = self.ax.yaxis.get_major_ticks()
                    if ticks:
                        ticks[-1].tick1line.set_markersize(0)

        # Если xname задан в set_config
        if self.config['xname'] is not None:
            # Если xname_ofst задан в set_config, то xname добавляется через ax.text()
            if self.config['xname_ofst'] is not None:
                # Положение головки стрелки оси X
                arrow_tip_x = xlim[1] - hl_x
                # Отступ для xname, отсчитываемый от конца стрелки
                xname_offset_x, xname_offset_y = self.config['xname_ofst']
                # Новое положение xname
                new_xname_pos_x = arrow_tip_x + xname_offset_x
                new_xname_pos_y = -xname_offset_y
                self.ax.text(new_xname_pos_x, new_xname_pos_y,
                             self.config['xname'], ha='right', va='top',
                             fontsize=self.config['fontsize'])
            else:
                current_xticks = list(self.ax.get_xticks())
                current_xlabels = [tick.get_text() for tick in self.ax.get_xticklabels()]

                # Определение положения для нового тика
                if self.config['xname_x'] is not None:
                    new_xtick = self.config['xname_x']
                #elif current_xticks:
                    #new_xtick = max(current_xticks) + (current_xticks[1] - current_xticks[0] if len(current_xticks) > 1 else 1)
                else:
                    new_xtick = xlim[1]

                # Добавляем xname как новый тик
                if new_xtick not in current_xticks:
                    current_xticks.append(new_xtick)
                    current_xlabels.append(self.config['xname'])

                    self.ax.set_xticks(current_xticks)
                    self.ax.set_xticklabels(current_xlabels)

                    # Удаляем штрих у новой метки
                    xticks = self.ax.xaxis.get_major_ticks()
                    if xticks:
                        xticks[-1].tick1line.set_markersize(0)


        # Добавление нуля у начала координат, если параметр 'zero' установлен в True
        if self.config.get('zero', True):

            zero_ofst = self.config.get('zero_ofst', [0.3, 0.3])

            if self.config['zero_ofst'] is None:
                # Добавляем ноль как новую метку по оси X
                current_xticks = list(self.ax.get_xticks())
                current_xlabels = [tick.get_text() for tick in self.ax.get_xticklabels()]
                if 0 not in current_xticks:
                    zero_x = self.config.get('zero_x', 0)
                    current_xticks.append(-zero_x)
                    current_xlabels.append("$0$")
                    self.ax.set_xticks(current_xticks)
                    self.ax.set_xticklabels(current_xlabels)
                    # Удаляем штрих у метки "0"
                    xticks = self.ax.xaxis.get_major_ticks()
                    if xticks:
                        xticks[current_xticks.index(-zero_x)].tick1line.set_markersize(0)

            else:
                # Используем zero_ofst для позиционирования нуля
                self.ax.text(-zero_ofst[0], -zero_ofst[1], '$0$',
                             fontsize=self.config['fontsize'], ha='right',
                             va='baseline')

        # Добавление сетки
        if self.config.get('grid', False):
            self._add_grid()

        plt.show()

    def save(self, filename, **kwargs):
        plt.margins(x=0,y=0, tight=True)
        self.fig.savefig(filename, bbox_inches='tight')

        # Trim whitespace using Inkscape. Removes groupes with ids patch_1 and patch_2
        if 'crop' in kwargs:
            if kwargs['crop']:
                inkscape_command = f'inkscape --actions="select-by-id:patch_1,patch_2;delete;select-all:all;fit-canvas-to-selection;export-filename:{filename};export-do;" {filename}'
                os.system(inkscape_command)
