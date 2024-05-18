import subprocess

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyArrowPatch

from .global_drawing import GLOBAL_DRAWING


class Drawing:
    def __init__(self):
        self.last_point = None
        self.config = {
            'font': 'stix',
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
            'axes_arrow_width': None,  # Set axes arrows width
            'axes_arrow_length': None,  # Set axes arrows length
            'axes_arrow_scale': 1,  # Scale axes arrows by a factor
            'arrow_size': 27,  # Default arrows size for processes
            'tick_width': None,
            'tick_length': None,
            'center_x': None,
            'center_y': None,
            'center': None,
            'y_gap': None,
            'y_gap_size': 0.05,
        }
        self.grid_config = {}  # Initialization of grid_config as an empty dictionary.
        self.fig = None
        self.ax = None

    def __enter__(self):
        GLOBAL_DRAWING.set(self)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if GLOBAL_DRAWING.drawing is self:
            GLOBAL_DRAWING.release_drawing()
        plt.close(self.fig)

    def __iadd__(self, process):
        self.add_process(process)
        return self

    ## For global drawing
    # def initialize_axes(self):
    ##self.fig, self.ax = plt.subplots()
    # pass

    def update_rcParams(self):
        tick_length = self.config['tick_length'] if self.config['tick_length'] is not None else 6.5
        tick_width = self.config['tick_width'] if self.config['tick_width'] is not None else 2
        plt.rcParams.update(
            {
                'font.size': self.config['fontsize'],
                'xtick.major.size': tick_length,
                'ytick.major.size': tick_length,
                'xtick.major.width': tick_width,
                'ytick.major.width': tick_width,
            }
        )
        if 'stix' in self.config.get('font', ''):
            plt.rcParams.update(
                {
                    'text.usetex': False,
                    'mathtext.fontset': 'custom',
                    'mathtext.it': 'STIX Two Text:italic',
                    'mathtext.rm': 'STIX Two Text',
                    'mathtext.sf': 'STIX Two Text',
                    'font.sans-serif': 'STIX Two Text',
                }
            )
        else:
            plt.rcParams.update(
                {
                    'text.usetex': True,
                    'font.family': 'serif',
                    'text.latex.preamble': '\n'.join(
                        [r'\usepackage[T2A]{fontenc}', r'\usepackage[utf8]{inputenc}', r'\usepackage[russian]{babel}']
                    ),
                }
            )

        # Create figure and axes
        self.fig, self.ax = plt.subplots()

        # Hide standard spines of a figure
        self.ax.spines['top'].set_visible(False)
        self.ax.spines['right'].set_visible(False)
        self.ax.spines['bottom'].set_visible(False)
        self.ax.spines['left'].set_visible(False)
        # Set zero at bottom left
        self.ax.spines['bottom'].set_position('zero')
        self.ax.spines['left'].set_position('zero')

        # Remove standard ticks
        self.ax.set_xticks([])
        self.ax.set_yticks([])

    def set_config(self, **kwargs):
        self.config.update(kwargs)
        self.update_rcParams()

        ## Set the axes limits if they have been specified.
        # if 'xlim' in kwargs:
        # self.ax.set_xlim(kwargs['xlim'])
        # if 'ylim' in kwargs:
        # self.ax.set_ylim(kwargs['ylim'])

    def add_process(self, process):
        if self.ax is None:
            raise Exception('Axes not initialized.')
        process.config = self.config  # Set config for the process
        if process.start is None and self.last_point is not None:
            # Use last point from the previous process
            # as an initial point for this process
            process.at(*self.last_point)

        # Plot the process
        process.plot(self.ax, self.config)

        # Add labels
        if hasattr(process, 'start_ytick_label'):
            self._add_ytick_label(process.start[1], process.start_ytick_label)
        if hasattr(process, 'end_ytick_label'):
            self._add_ytick_label(process.end[1], process.end_ytick_label)
        if hasattr(process, 'start_xtick_label'):
            self._add_xtick_label(process.start[0], process.start_xtick_label)
        if hasattr(process, 'end_xtick_label'):
            self._add_xtick_label(process.end[0], process.end_xtick_label)

        # Add aditional lines (tox, toy, tozero)
        for line_type, line_part, color, ls, lw in process.extra_lines:
            start_x, start_y = process.start if process.start else (None, None)
            end_x, end_y = process.end if process.end else (None, None)

            if line_type == 'x':
                if line_part in ['both', 'start'] and start_x is not None:
                    self.ax.plot([start_x, start_x], [start_y, 0], color=color, linestyle=ls, linewidth=lw)
                if line_part in ['both', 'end'] and end_x is not None:
                    self.ax.plot([end_x, end_x], [end_y, 0], color=color, linestyle=ls, linewidth=lw)
            # Similarly for 'y'
            elif line_type == 'y':
                if line_part in ['both', 'start'] and start_y is not None:
                    self.ax.plot([start_x, 0], [start_y, start_y], color=color, linestyle=ls, linewidth=lw)
                if line_part in ['both', 'end'] and end_y is not None:
                    self.ax.plot([end_x, 0], [end_y, end_y], color=color, linestyle=ls, linewidth=lw)
            # Similarly for 'zero'
            elif line_type == 'zero':
                if line_part in ['both', 'start'] and start_x is not None and start_y is not None:
                    self.ax.plot([0, start_x], [0, start_y], color=color, linestyle=ls, linewidth=lw)
                if line_part in ['both', 'end'] and end_x is not None and end_y is not None:
                    self.ax.plot([0, end_x], [0, end_y], color=color, linestyle=ls, linewidth=lw)

        # Update the last point so the next process can use it as its starting point.
        if process.end is not None:
            self.last_point = process.end

    def grid(
        self,
        step=None,
        step_x=None,
        step_y=None,
        ls='-',
        color='#777777',
        lw=0.9,
        zorder=-9,
        Nx=None,
        Ny=None,
        x_start=None,
        x_end=None,
        y_start=None,
        y_end=None,
    ):
        # Ignore step_x и step_y, if 'step' is set
        if step is not None:
            if step_x is not None or step_y is not None:
                print("Warning: 'step_x' and 'step_y' are ignored because 'step' is set.")
            step_x = step_y = step

        # Default grid configuration (step_x, step_y, y_end, x_end, Nx, Ny)
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

    # Draw a grid
    def _add_grid(self):
        xlim = self.config.get('xlim', self.ax.get_xlim())
        ylim = self.config.get('ylim', self.ax.get_ylim())

        grid_config = self.grid_config
        Nx = grid_config.get('Nx', int((xlim[1] - xlim[0]) // grid_config.get('step_x', 5)) - 1)
        Ny = grid_config.get('Ny', int((ylim[1] - ylim[0]) // grid_config.get('step_y', 5)))

        # Calculate range and step for a grid
        x_step = grid_config['step_x']
        y_step = grid_config['step_y']

        x_start = grid_config.get('x_start', max(xlim[0], 0 - (Nx // 2) * x_step))
        x_end = grid_config.get('x_end', min(xlim[1], x_start + Nx * x_step))
        if ylim[0] >= 0:
            y_start = grid_config.get('y_start', y_step * (ylim[0] // y_step))
        else:
            y_start = grid_config.get('y_start', y_step * (ylim[0] // y_step + 1))
        y_end = grid_config.get('y_end', min(ylim[1], y_start + Ny * y_step))

        # Draw vertical lines
        for x in np.arange(x_start, x_end + grid_config['step_x'], grid_config['step_x']):
            if x != 0 and xlim[0] <= x <= min(
                xlim[1], x_end
            ):  # Учитываем x_end и игнорируем линию, совпадающую с осью Y
                self.ax.plot(
                    [x, x],
                    [y_start, y_end],
                    linestyle=grid_config['ls'],
                    color=grid_config['color'],
                    linewidth=grid_config['lw'],
                    zorder=grid_config['zorder'],
                    clip_on=False,
                )

        # Draw horizontal lines
        for y in np.arange(y_start, y_end + y_step, y_step):
            if y != 0 and ylim[0] <= y <= min(
                ylim[1], y_end
            ):  # Учитываем y_end и игнорируем линию, совпадающую с осью X
                self.ax.plot(
                    [x_start, x_end],
                    [y, y],
                    linestyle=grid_config['ls'],
                    color=grid_config['color'],
                    linewidth=grid_config['lw'],
                    zorder=grid_config['zorder'],
                    clip_on=False,
                )

    def _add_xtick_label(self, x, label):
        xlen = self.config['xlim'][1] - self.config['xlim'][0]
        ylen = self.config['ylim'][1] - self.config['ylim'][0]
        xlabel_ofst = self.config.get('xlabel_ofst', [xlen * 0.02, ylen * 0.14 * self.config['fontsize'] / 30])
        if self.config['tick_length'] is not None:
            tick_length = self.config['tick_length']
        else:
            tick_length = xlabel_ofst[1] * 0.2
        # Add label text
        self.ax.text(x, -xlabel_ofst[1], label, va='baseline', ha='center', fontsize=self.config['fontsize'])
        # Draw a tick line
        self.ax.plot(
            [x, x], [0, -tick_length], color='k', linestyle='-', linewidth=self.config['lw'] * 0.8, clip_on=False
        )

    def _add_ytick_label(self, y_val, label):
        xlen = self.config['xlim'][1] - self.config['xlim'][0]
        ylen = self.config['ylim'][1] - self.config['ylim'][0]
        aspect = self.config['aspect']

        ylabel_ofst = self.config.get('ylabel_ofst', [xlen * 0.05 * aspect, ylen * 0.03])
        xlabel_ofst = self.config.get('xlabel_ofst', [xlen * 0.02, ylen * 0.14 * self.config['fontsize'] / 30])
        if self.config['tick_length'] is not None:
            tick_length = self.config['tick_length']
        else:
            tick_length = xlabel_ofst[1] * 0.2 * aspect

        # Add label text
        self.ax.text(-ylabel_ofst[0], y_val, label, va='center', ha='right', fontsize=self.config['fontsize'])
        # Draw a tick line
        self.ax.plot(
            [-tick_length, 0],
            [y_val, y_val],
            color='k',
            linestyle='-',
            linewidth=self.config['lw'] * 0.8,
            clip_on=False,
        )

    def add_xticks(self, xticks, names=None, bg=False, bgcolor='white', bgsize=None, direction='out'):
        ylen = self.config['ylim'][1] - self.config['ylim'][0]
        xlen = self.config['xlim'][1] - self.config['xlim'][0]
        xlabel_ofst = self.config.get('xlabel_ofst', [xlen * 0.02, ylen * 0.14 * self.config['fontsize'] / 30])

        if self.config['tick_length'] is None:
            tick_length = xlabel_ofst[1] * 0.2
        else:
            tick_length = self.config['tick_length']

        # If 'names' is set. Example: d.add_xticks([1,2,3], names=['a','b','c']
        if names is not None and len(names) == len(xticks):
            label_dict = dict(zip(xticks, names))
        else:
            label_dict = {}

        for x in xticks:
            # Replace value with a corresponding name
            x_label = label_dict.get(x, x)
            # Replace . for a comma as a decimal separator
            if isinstance(x, (int, float)):
                x_label = f'{x_label}'.replace('.', ',')
            # Оборачиваем метку в LaTeX
            # x_label = f"${x_label}$"

            if bg:
                # Set background for a ticklabel
                bg_params = {'boxstyle': 'round,pad=0.1', 'facecolor': bgcolor, 'edgecolor': 'none', 'alpha': 1}
                if bgsize:
                    bg_params['boxstyle'] = f'round,pad={bgsize}'
                # Add the text with a background
                self.ax.text(
                    x,
                    -xlabel_ofst[1],
                    x_label,
                    va='baseline',
                    ha='center',
                    fontsize=self.config['fontsize'],
                    bbox=bg_params,
                )
            else:
                # Add the text without a background
                self.ax.text(x, -xlabel_ofst[1], x_label, va='baseline', ha='center', fontsize=self.config['fontsize'])

            # Рисование штриха
            if direction == 'out':
                end = -tick_length
            elif direction == 'in':
                end = tick_length
            else:
                end = 0

            self.ax.plot([x, x], [0, end], color='k', linestyle='-', linewidth=self.config['lw'] * 0.8, clip_on=False)

    def add_yticks(self, yticks, names=None, direction='out'):
        aspect = self.config['aspect']
        xlen = self.config['xlim'][1] - self.config['xlim'][0]
        ylen = self.config['ylim'][1] - self.config['ylim'][0]
        ylabel_ofst = self.config.get('ylabel_ofst', [xlen * 0.05 * aspect, ylen * 0.03])
        xlabel_ofst = self.config.get('xlabel_ofst', [xlen * 0.02, ylen * 0.14 * self.config['fontsize'] / 30])

        if self.config['tick_length'] is None:
            tick_length = xlabel_ofst[1] * 0.2
        else:
            tick_length = self.config['tick_length']

        # If 'names' is set. Example: d.add_yticks([1,2,3], names=['a','b','c']
        if names is not None and len(names) == len(yticks):
            label_dict = dict(zip(yticks, names))
        else:
            label_dict = {}

        for y in yticks:
            # Replace value with a corresponding name
            y_label = label_dict.get(y, y)
            # Replace . for a comma as a decimal separator
            if isinstance(y, (int, float)):
                y_label = f'{y_label}'.replace('.', ',')
            y_label = f'${y_label}$'
            self.ax.text(-ylabel_ofst[0], y, y_label, va='center', ha='right', fontsize=self.config['fontsize'])

            # Draw a tick line
            if direction == 'out':
                start = -tick_length * aspect
            elif direction == 'in':
                start = tick_length * aspect
            else:
                start = 0

            self.ax.plot([start, 0], [y, y], 'k-', clip_on=False, linewidth=self.config['lw'] * 0.8)

    def show(self):
        if GLOBAL_DRAWING.drawing is self:
            GLOBAL_DRAWING.release_processes()

        xlen = self.config['xlim'][1] - self.config['xlim'][0]
        ylen = self.config['ylim'][1] - self.config['ylim'][0]
        lw = self.config['lw'] * 0.8

        xlim = self.config.get('xlim', self.ax.get_xlim())
        ylim = self.config.get('ylim', self.ax.get_ylim())

        # Set aspect
        if 'aspect' in self.config:
            self.ax.set_aspect(self.config['aspect'])
            aspect = self.config['aspect']
        else:
            aspect = 1

        # Draw axes with arrows
        longer_axis = np.amax([xlen, ylen])
        k = 1 / 2
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

        ## X axis
        # arrowstyle_x = f"-|>,head_length={hl_x},head_width={hw_x}"
        # arrow_x = FancyArrowPatch((xlim[0], 0), (xlim[1], 0),
        # clip_on=False,
        # arrowstyle=arrowstyle_x,
        # mutation_scale = 200 / xlen * axes_arrow_scale,
        # mutation_aspect=aspect,
        # shrinkA=0,
        # shrinkB=0,
        # lw=lw, color='k', zorder=5)
        # self.ax.add_patch(arrow_x)

        # Set x_gap
        x_gap = self.config.get('x_gap', None)
        x_gap_size = self.config.get('x_gap_size', 0.05) * xlen
        x_gap_margin = x_gap_size * 0.5  # Small gap before and after the dots

        if x_gap is not None:
            arrow_x_segments = [
                ((xlim[0], 0), (x_gap - x_gap_size / 2 - x_gap_margin, 0)),
                ((x_gap + x_gap_size / 2 + x_gap_margin, 0), (xlim[1] - hl_x, 0)),  # Adjust to avoid double arrow
            ]
        else:
            arrow_x_segments = [((xlim[0], 0), (xlim[1] - hl_x, 0))]  # Adjust to add arrow

        # Draw X axis segments
        arrowstyle_x = f'-|>,head_length={hl_x},head_width={hw_x}'
        for i, (start, end) in enumerate(arrow_x_segments):
            if i == len(arrow_x_segments) - 1:
                # Add arrow to the last segment
                arrow_x = FancyArrowPatch(
                    start,
                    end,
                    clip_on=False,
                    arrowstyle=arrowstyle_x,
                    mutation_scale=200 / xlen * axes_arrow_scale,
                    mutation_aspect=aspect,
                    shrinkA=0,
                    shrinkB=0,
                    lw=lw,
                    color='k',
                    zorder=5,
                )
            else:
                # Add regular line segments
                arrow_x = FancyArrowPatch(
                    start,
                    end,
                    clip_on=False,
                    arrowstyle='-',
                    mutation_scale=200 / xlen * axes_arrow_scale,
                    mutation_aspect=aspect,
                    shrinkA=0,
                    shrinkB=0,
                    lw=lw,
                    color='k',
                    zorder=5,
                )
            self.ax.add_patch(arrow_x)

        # Add dots to indicate the gap on X axis
        if x_gap is not None:
            dot_size = lw * 1.2  # Adjust dot size
            self.ax.plot(x_gap - x_gap_size / 2, 0, 'ko', markersize=dot_size, clip_on=False)
            self.ax.plot(x_gap, 0, 'ko', markersize=dot_size, clip_on=False)
            self.ax.plot(x_gap + x_gap_size / 2, 0, 'ko', markersize=dot_size, clip_on=False)

            # Add small gaps before and after the dots
            self.ax.plot(
                x_gap - x_gap_size / 2 - x_gap_margin, 0, 'w|', markersize=dot_size * 1.5, clip_on=False, linewidth=lw
            )
            self.ax.plot(
                x_gap + x_gap_size / 2 + x_gap_margin, 0, 'w|', markersize=dot_size * 1.5, clip_on=False, linewidth=lw
            )

        # Set y_gap
        y_gap = self.config['y_gap']
        y_gap_size = self.config['y_gap_size'] * ylen
        gap_margin = y_gap_size * 0.5  # Small gap before and after the dots

        if y_gap is not None:
            arrow_y_segments = [
                ((0, ylim[0]), (0, y_gap - y_gap_size / 2 - gap_margin)),
                ((0, y_gap + y_gap_size / 2 + gap_margin), (0, ylim[1] - 0.08)),  # Adjust to avoid double arrow
            ]
        else:
            arrow_y_segments = [((0, ylim[0]), (0, ylim[1] - 0.08))]  # Adjust to add arrow

        # Y axis segments
        arrowstyle_y = f'-|>,head_length={hl_y},head_width={hw_y}'
        for i, (start, end) in enumerate(arrow_y_segments):
            if i == len(arrow_y_segments) - 1:
                # Add arrow to the last segment
                arrow_y = FancyArrowPatch(
                    start,
                    end,
                    clip_on=False,
                    arrowstyle=arrowstyle_y,
                    mutation_scale=200 / xlen * axes_arrow_scale,
                    mutation_aspect=aspect,
                    shrinkA=0,
                    shrinkB=0,
                    lw=lw,
                    color='k',
                    zorder=5,
                )
            else:
                # Add regular line segments
                arrow_y = FancyArrowPatch(
                    start,
                    end,
                    clip_on=False,
                    arrowstyle='-',
                    mutation_scale=200 / xlen * axes_arrow_scale,
                    mutation_aspect=aspect,
                    shrinkA=0,
                    shrinkB=0,
                    lw=lw,
                    color='k',
                    zorder=5,
                )
            self.ax.add_patch(arrow_y)

        # Add dots to indicate the gap
        if y_gap is not None:
            dot_size = lw * 1.2  # Adjust dot size
            self.ax.plot(0, y_gap - y_gap_size / 2, 'ko', markersize=dot_size, clip_on=False)
            self.ax.plot(0, y_gap, 'ko', markersize=dot_size, clip_on=False)
            self.ax.plot(0, y_gap + y_gap_size / 2, 'ko', markersize=dot_size, clip_on=False)

            # Add small gaps before and after the dots
            self.ax.plot(
                0, y_gap - y_gap_size / 2 - gap_margin, 'w|', markersize=dot_size * 1.5, clip_on=False, linewidth=lw
            )
            self.ax.plot(
                0, y_gap + y_gap_size / 2 + gap_margin, 'w|', markersize=dot_size * 1.5, clip_on=False, linewidth=lw
            )

        # Set labels padding. Used in d.add_xticks() but NOT in d.ax.add_xticks()
        xlabel_ofst = self.config.get('xlabel_ofst', [xlen * 0.02, ylen * 0.14 * self.config['fontsize'] / 30])
        ylabel_ofst = self.config.get('ylabel_ofst', [xlen * 0.05 * aspect, ylen * 0.03])

        # Add axis labels xname, yname. If xname_ofst, yname_ofst are not
        # specified, then yname is vertically aligned with ylabels, and xname
        # is horizontally aligned with xlabels.
        if self.config['xname_ofst'] is None:
            x_dx = xlabel_ofst[0]
            x_dy = -xlabel_ofst[1]
        else:
            x_dx = self.config['xname_ofst'][0]
            x_dy = self.config['xname_ofst'][1]

        # If yname is specified in set_config, add it as a new tick and remove
        # the tick mark. If yname_y is specified in set_config, add it as a new
        # tick at the y coordinate and remove the tick mark. If yname_ofst is
        # specified in set_config, then yname is added not as a tick mark but
        # through ax.text()
        if self.config['yname'] is not None:
            # If yname_ofst is specified in set_config, then yname is added via ax.text()
            if self.config['yname_ofst'] is not None:
                arrow_tip_y = ylim[1] - hl_y
                # Offset for yname, measured from the end of the arrow.
                yname_offset_x, yname_offset_y = self.config['yname_ofst']
                # New yname position
                new_yname_pos_x = -yname_offset_x
                new_yname_pos_y = arrow_tip_y + yname_offset_y
                self.ax.text(
                    new_yname_pos_x,
                    new_yname_pos_y,
                    self.config['yname'],
                    ha='right',
                    va='top',
                    fontsize=self.config['fontsize'],
                )
            else:
                current_ticks = list(self.ax.get_yticks())
                current_labels = [tick.get_text() for tick in self.ax.get_yticklabels()]

                # Set 'yname' tick at new position if specified
                if self.config['yname_y'] is not None:
                    new_tick = self.config['yname_y']
                else:
                    new_tick = ylim[1]

                # Add yname as a new ytick
                if new_tick not in current_ticks:
                    current_ticks.append(new_tick)
                    current_labels.append(self.config['yname'])
                    self.ax.set_yticks(current_ticks)
                    self.ax.set_yticklabels(current_labels)

                    # Remove a tickmark at yname tick
                    ticks = self.ax.yaxis.get_major_ticks()
                    if ticks:
                        ticks[-1].tick1line.set_markersize(0)

        # Similarly for xname
        if self.config['xname'] is not None:
            # If xname_ofst is specified in set_config, then yname is added via ax.text()
            if self.config['xname_ofst'] is not None:
                arrow_tip_x = xlim[1] - hl_x
                # Offset for xname, measured from the end of the arrow.
                xname_offset_x, xname_offset_y = self.config['xname_ofst']
                # New xname position
                new_xname_pos_x = arrow_tip_x + xname_offset_x
                new_xname_pos_y = -xname_offset_y
                self.ax.text(
                    new_xname_pos_x,
                    new_xname_pos_y,
                    self.config['xname'],
                    ha='right',
                    va='top',
                    fontsize=self.config['fontsize'],
                )
            else:
                current_xticks = list(self.ax.get_xticks())
                current_xlabels = [tick.get_text() for tick in self.ax.get_xticklabels()]

                # Set 'xname' tick at new position if specified
                if self.config['xname_x'] is not None:
                    new_xtick = self.config['xname_x']
                else:
                    new_xtick = xlim[1]

                # Add yname as a new ytick
                if new_xtick not in current_xticks:
                    current_xticks.append(new_xtick)
                    current_xlabels.append(self.config['xname'])
                    self.ax.set_xticks(current_xticks)
                    self.ax.set_xticklabels(current_xlabels)

                    # Remove a tickmark at yname tick
                    xticks = self.ax.xaxis.get_major_ticks()
                    if xticks:
                        xticks[-1].tick1line.set_markersize(0)

        # Add a zero at the origin if the 'zero' parameter is set to True. If
        # zero_ofst is set, then zero is added via ax.text(). Otherwise, it is
        # added as an x-axis label without a tick mark.
        # 'zero_x' shifts zero to the left.
        # Use zero=False in set_config to remove zero
        if self.config.get('zero', True):
            zero_ofst = self.config.get('zero_ofst', [0.3, 0.3])

            if self.config['zero_ofst'] is None:
                # Add zero as a new x tick
                current_xticks = list(self.ax.get_xticks())
                current_xlabels = [tick.get_text() for tick in self.ax.get_xticklabels()]
                if 0 not in current_xticks:
                    zero_x = self.config.get('zero_x', 0)
                    current_xticks.append(-zero_x)
                    current_xlabels.append('$0$')
                    self.ax.set_xticks(current_xticks)
                    self.ax.set_xticklabels(current_xlabels)
                    # Remove the tick at zero
                    xticks = self.ax.xaxis.get_major_ticks()
                    if xticks:
                        xticks[current_xticks.index(-zero_x)].tick1line.set_markersize(0)

            else:
                # Use zero_ofst for positioning zero with ax.text()
                self.ax.text(
                    -zero_ofst[0], -zero_ofst[1], '$0$', fontsize=self.config['fontsize'], ha='right', va='baseline'
                )

        # Draw grid
        if self.config.get('grid', False):
            self._add_grid()

        plt.show()

    def save(self, filename, **kwargs):
        plt.margins(x=0, y=0, tight=True)
        self.fig.savefig(filename, bbox_inches='tight')

        # Trim whitespace using Inkscape if 'crop' is specified and True
        if kwargs.get('crop', False):
            inkscape_command = [
                'inkscape',
                '--actions',
                'select-by-id:patch_1,patch_2;delete;select-all:all;fit-canvas-to-selection;export-filename:'
                + filename
                + ';export-do;',
                filename,
            ]
            subprocess.run(inkscape_command)
