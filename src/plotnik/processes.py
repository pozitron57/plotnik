import numpy as np
from matplotlib.patches import ArrowStyle, FancyArrowPatch
from scipy.interpolate import interp1d

from .global_drawing import GLOBAL_DRAWING


# Process() is a parent class for
# Linear(), Power(), Iso_t(), Adiabatic(), Bezier() subclasses.
class Process:
    def __init__(self):
        self.start = None
        self.end = None
        self.color = 'k'
        self.arrow_params = {}
        self.dots_params = {'start': None, 'end': None}
        self.linestyle = '-'
        self.zorder = 1
        self.linewidth = 2.5
        self.extra_lines = []  # to store tox(), toy(), tozero() information
        self.xtick_labels = []
        self.ytick_labels = []
        self._add_to_global_drawing()

    def _add_to_global_drawing(self):
        try:
            self.start = GLOBAL_DRAWING.last_point()
            GLOBAL_DRAWING.store_process(self)
        except ValueError:
            pass

    def at(self, start_x, start_y):
        self.start = (start_x, start_y)
        return self

    def to(self, end_x, end_y=None):
        self.end = (end_x, end_y)
        return self

    def arrow(
        self, size=None, pos=0.54, color='black', reverse=False, filled=True, zorder=3, head_length=0.6, head_width=0.2
    ):
        self.arrow_params = {
            'size': size,
            'pos': pos,
            'color': color,
            'reverse': reverse,
            'filled': filled,
            'zorder': zorder,
            'head_length': head_length,
            'head_width': head_width,
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

            # Calculate arrow rotation
            if index < len(x_values) - 1:
                dx = x_values[index + 1] - x
                dy = y_values[index + 1] - y
            else:
                dx = x - x_values[index - 1]
                dy = y - y_values[index - 1]

            # Reverse the arrow
            if self.arrow_params['reverse']:
                dx, dy = -dx, -dy

            # Arrow style
            if self.arrow_params['filled']:
                style = ArrowStyle(
                    '-|>', head_length=self.arrow_params['head_length'], head_width=self.arrow_params['head_width']
                )
            else:
                style = ArrowStyle(
                    '->', head_length=self.arrow_params['head_length'], head_width=self.arrow_params['head_width']
                )

            # Draw arrow
            arrow = FancyArrowPatch(
                (x, y),
                (x + dx, y + dy),
                arrowstyle=style,
                color=self.arrow_params['color'],
                mutation_scale=arrow_size,
                zorder=self.arrow_params['zorder'],
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

    def zord(self, zorder):
        self.zorder = zorder
        return self

    def dot(self, pos='end', **kwargs):
        default_params = {'size': 8, 'color': 'black', 'zorder': 5}
        # Add user specified parameters to default parameters
        dot_params = {**default_params, **kwargs}

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
                # Check that point has 2 coordinates
                if point and None not in point:
                    ax.plot(
                        point[0],
                        point[1],
                        marker=self.dots_params[position].get('marker', 'o'),
                        markersize=self.dots_params[position].get('size', 6),
                        color=self.dots_params[position].get('color', 'k'),
                        zorder=self.dots_params[position].get('zorder', '5'),
                    )

    def calculate_ofst(self, point=None):
        # Check that config is accessible
        if not hasattr(self, 'config') or not self.config:
            raise ValueError('Config not set for this process.')

        xlen = self.config['xlim'][1] - self.config['xlim'][0]
        ylen = self.config['ylim'][1] - self.config['ylim'][0]

        if self.config['center']:
            center_x, center_y = self.config['center']
        else:
            center_x = self.config['center_x'] if self.config['center_x'] else xlen / 2
            center_y = self.config['center_y'] if self.config['center_y'] else ylen / 2

        # Calculate the offset depending on the point's position
        k = self.config['fontsize'] / 27
        dx = xlen * 0.05 * k if point and point[0] >= center_x else -xlen * 0.05 * k
        dy = ylen * 0.06 * k if point and point[1] >= center_y else -ylen * 0.07 * k

        return (dx, dy)

    def label(
        self,
        text1=None,
        text2=None,
        ofst=None,
        start_ofst=None,
        end_ofst=None,
        end_dx=None,
        end_dy=None,
        start_dx=None,
        start_dy=None,
        dx=None,
        dy=None,
    ):
        # Set dx and dy if they are provided
        if dx is not None:
            start_dx = end_dx = dx
        if dy is not None:
            start_dy = end_dy = dy

        # Set start_ofst and end_ofst considering individual offsets
        if start_ofst is None and (start_dx is not None or start_dy is not None):
            start_ofst = (start_dx, start_dy)

        if end_ofst is None and (end_dx is not None or end_dy is not None):
            end_ofst = (end_dx, end_dy)

        # Set ofst if it is provided
        if ofst is not None:
            start_ofst = end_ofst = ofst

        # Setting labels for State or for the start and end points
        if isinstance(self, State):
            self.start_label = {'text': text1, 'ofst': start_ofst}
        else:
            if text2 is None:
                self.start_label = {'text': text1, 'ofst': start_ofst}
            else:
                self.start_label = {'text': text1, 'ofst': start_ofst}
                self.end_label = {'text': text2, 'ofst': end_ofst}
        return self

    def _add_labels(self, ax, config):
        def add_label(point, label_data, ax, config):
            if label_data['ofst'] is None:
                dx, dy = self.calculate_ofst(point)
            else:
                dx, dy = label_data['ofst']
                # If dx or dy are not provided, use default values
                if dx is None or dy is None:
                    default_dx, default_dy = self.calculate_ofst(point)
                    dx = dx if dx is not None else default_dx
                    dy = dy if dy is not None else default_dy

            ax.text(
                point[0] + dx, point[1] + dy, label_data['text'], fontsize=config['fontsize'], ha='center', va='center'
            )

        if hasattr(self, 'start_label') and self.start:
            add_label(self.start, self.start_label, ax, config)

        if hasattr(self, 'end_label') and self.end:
            add_label(self.end, self.end_label, ax, config)

    # For Bezier().connect() to work
    def tangent_at_end(self):
        if hasattr(self, 'x_values') and hasattr(self, 'y_values') and len(self.x_values) > 1:
            # Use the last two points to determine the tangent
            direction = (self.x_values[-1] - self.x_values[-2], self.y_values[-1] - self.y_values[-2])
            return direction
        return None

    def tangent_at_start(self):
        if hasattr(self, 'x_values') and hasattr(self, 'y_values') and len(self.x_values) > 1:
            # Use the first two points to determine the tangent
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
        # Function to convert a number to a string with a dot replaced by a comma
        def format_label(value):
            return f'${str(value).replace(".", "{,}")}$'

        # If labels are not provided, use the numerical values of the coordinates
        if not labels:
            if isinstance(self, State) or which == 'start':
                self.start_xtick_label = format_label(self.start[0])
            elif which == 'end' and self.end is not None:
                self.end_xtick_label = format_label(self.end[0])
            elif self.end is not None:
                # Add labels for both points
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
        # Function to convert a number to a string, replacing a dot with a comma
        def format_label(value):
            return f'${str(value).replace(".", "{,}")}$'

        # If labels are not provided, use the numerical values of the coordinates
        if not labels:
            if isinstance(self, State) or which == 'start':
                self.start_ytick_label = format_label(self.start[1])
            elif which == 'end' and self.end is not None:
                self.end_ytick_label = format_label(self.end[1])
            elif self.end is not None:
                # Adding labels for both points
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
            ax.plot(
                self.x_values,
                self.y_values,
                color=self.color,
                linestyle=self.linestyle,
                linewidth=self.linewidth,
                zorder=self.zorder,
            )
            if self.arrow_params:
                self._add_arrow(ax, self.x_values, self.y_values)
            self._add_dots(ax)
        # Add labels
        self._add_labels(ax, config)


class State(Process):
    def __init__(self, drawing=None):
        super().__init__()  # Call the constructor of the parent class
        self.draw_dot = False  # Flag to control the drawing of the point
        self.type = 'state'
        self.dot_params = {'size': 6, 'color': 'black'}  # Default params for the point
        self.label_text = ''
        self.label_ofst = None
        if drawing:
            self.ax = drawing.ax
            self.config = drawing.config
        else:
            self.ax = None
            self.config = {}

    def at(self, x, y):
        self.start = (x, y)  # For State, there's only a start point (same as the end point)
        return self

    def dot(self, size=6, color='k'):
        self.dot_params = {'size': size, 'color': color}
        self.draw_dot = True
        return self

    def plot(self, ax, config):
        if self.start is None:
            raise ValueError('Start point not set for State.')

        x, y = self.start

        # Drawing the point
        if self.draw_dot:
            ax.plot(x, y, 'o', markersize=self.dot_params['size'], color=self.dot_params['color'])

        ## If a label is provided, draw it
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
        # if self.start is None:
        # if self.drawing and self.drawing.last_point:
        # self.start = self.drawing.last_point
        # else:
        # raise ValueError("Start point must be set for 'Iso_t' process.")

        V1, p1 = self.start

        # If the end point is not defined, use parameters from the to() method
        if self.end is None:
            raise ValueError("End point must be set for 'Iso_t' process.")

        V2, p2 = self.end

        self.x_values = np.linspace(V1, V2, 100)
        self.y_values = p1 * V1 / self.x_values
        super().plot(ax, config)

    def to(self, end, end_type='pressure'):
        V1, p1 = self.start

        if end_type == 'pressure':
            p2 = end
            V2 = p1 * V1 / p2
        elif end_type == 'volume':
            V2 = end
            p2 = p1 * V1 / V2
        else:
            raise ValueError(f"Unknown end_type '{end_type}'")

        self.end = V2, p2
        return self


class Power(Process):
    def __init__(self, power=2, drawing=None):
        super().__init__()
        self.type = 'power'
        self.power = power

    def plot(self, ax, config):
        x1, y1 = self.start

        # If the end point is not defined, use parameters from the to() method
        if self.end is None:
            raise ValueError("End point must be set for 'Power' process.")

        x2, y2 = self.end

        # y = kx^n + b
        # Solving the system of equations to find k and b
        k = (y2 - y1) / (x2**self.power - x1**self.power)
        b = y1 - k * x1**self.power
        self.x_values = np.linspace(x1, x2, 100)
        self.y_values = k * self.x_values**self.power + b

        super().plot(ax, config)

    def to(self, end, end_type='x'):
        x1, y1 = self.start

        if end_type == 'x':
            x2 = end
            y2 = y1 * (x2 / x1) ** self.power
        elif end_type == 'y':
            y2 = end
            x2 = (y2 / y1) ** (1 / self.power) * x1
        else:
            x2 = end
            y2 = end_type

        self.end = x2, y2

        return self


class Adiabatic(Process):
    def __init__(self, gamma=5 / 3):
        super().__init__()
        self.gamma = gamma
        self.type = 'adiabatic'

    def plot(self, ax, config):
        # if self.start is None:
        # if self.drawing and self.drawing.last_point:
        # self.start = self.drawing.last_point
        # else:
        # raise ValueError("Start point must be set for 'Adiabatic' process.")

        V1, p1 = self.start

        # If the end point is not defined, use parameters from the to() method
        if self.end is None:
            raise ValueError("End point must be set for 'Adiabatic' process.")

        V2, p2 = self.end

        self.x_values = np.linspace(V1, V2, 100)
        self.y_values = (p1 * V1**self.gamma) / self.x_values**self.gamma
        super().plot(ax, config)

    def to(self, end, end_type='pressure'):
        V1, p1 = self.start

        if end_type == 'pressure':
            p2 = end
            V2 = (p1 * V1**self.gamma / p2) ** (1 / self.gamma)
        elif end_type == 'volume':
            V2 = end
            p2 = (p1 * V1**self.gamma) / V2**self.gamma
        else:
            raise ValueError(f"Unknown end_type '{end_type}'")

        self.end = V2, p2
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
        self.coordinates = []  # List to store the coordinates

    def connect(self, process1, process2):
        # Find the intersection point
        intersection_point = self._find_intersection(process1, process2)

        # Set the start and end points, as well as the control point
        self.start = process1.end if process1.end else process1.start
        self.end = process2.start if process2.start else process2.end
        self.x = intersection_point[0]
        self.y = intersection_point[1]

        return self

    def _find_intersection(self, process1, process2):
        tangent1 = process1.tangent_at_end()
        tangent2 = process2.tangent_at_start()

        if tangent1 is None or tangent2 is None:
            return None  # Impossible to calculate the intersection point

        x1, y1 = process1.end
        x2, y2 = x1 + tangent1[0], y1 + tangent1[1]
        x3, y3 = process2.start
        x4, y4 = x3 + tangent2[0], y3 + tangent2[1]

        # Calculating the slope coefficients
        k1 = (y2 - y1) / (x2 - x1)
        k2 = (y4 - y3) / (x4 - x3)

        # Calculating the intersection points with the Y-axis
        b1 = y1 - k1 * x1
        b2 = y3 - k2 * x3

        # Check for parallelism
        if k1 == k2:
            # Processes are parallel, need to choose another way of connection
            return None

        # Find the intersection point of the processes
        intersection_x = (b2 - b1) / (k1 - k2)
        intersection_y = k1 * intersection_x + b1

        return intersection_x, intersection_y

    def plot(self, ax, config):
        # Needed to store x_values
        if self.start and self.end:  # Why this check? What happens else?
            x1, y1 = self.start
            x2, y2 = self.end
            t = np.linspace(0, 1, 100)

            if self.x1 is not None and self.x2 is not None:
                # Third-order Bezier curve
                self.x_values = (
                    (1 - t) ** 3 * x1 + 3 * (1 - t) ** 2 * t * self.x1 + 3 * (1 - t) * t**2 * self.x2 + t**3 * x2
                )
                self.y_values = (
                    (1 - t) ** 3 * y1 + 3 * (1 - t) ** 2 * t * self.y1 + 3 * (1 - t) * t**2 * self.y2 + t**3 * y2
                )
            else:
                # Second-order Bezier curve
                self.x_values = (1 - t) ** 2 * x1 + 2 * (1 - t) * t * self.x + t**2 * x2
                self.y_values = (1 - t) ** 2 * y1 + 2 * (1 - t) * t * self.y + t**2 * y2

            super().plot(ax, config)

    def get_point(self, n):
        if self.start and self.end:  # Why this check? What happens else?
            x1, y1 = self.start
            x2, y2 = self.end
            t = np.linspace(0, 1, 100)

            if self.x1 is not None and self.x2 is not None:
                # Third-order Bezier curve
                self.x_values = (
                    (1 - t) ** 3 * x1 + 3 * (1 - t) ** 2 * t * self.x1 + 3 * (1 - t) * t**2 * self.x2 + t**3 * x2
                )
                self.y_values = (
                    (1 - t) ** 3 * y1 + 3 * (1 - t) ** 2 * t * self.y1 + 3 * (1 - t) * t**2 * self.y2 + t**3 * y2
                )
            else:
                # Second-order Bezier curve
                self.x_values = (1 - t) ** 2 * x1 + 2 * (1 - t) * t * self.x + t**2 * x2
                self.y_values = (1 - t) ** 2 * y1 + 2 * (1 - t) * t * self.y + t**2 * y2

            self.coordinates = list(zip(self.x_values, self.y_values))
        if 0 <= n < len(self.coordinates):
            return self.coordinates[n][0], self.coordinates[n][1]
        else:
            raise IndexError('Index out of the range of Bezier curve points.')

    def get_coordinates(self):
        self.coordinates = list(zip(self.x_values, self.y_values))
        if self.coordinates:
            # Split the list of tuples into two lists for x and y coordinates
            x_values, y_values = zip(*self.coordinates)
            return x_values, y_values
        else:
            return [], []  # Return empty lists if there are no coordinates


class Parabola(Process):
    def __init__(self):
        super().__init__()
        self.type = 'parabola'
        self.vertex_x = None
        self.vertex_y = None
        self.a = None
        self.b = None
        self.c = None

    def vertex(self, x0, y0):
        self.vertex_x = x0
        self.vertex_y = y0
        return self

    def calculate_coefficients(self):
        # Убедитесь, что все точки заданы
        if self.vertex_x is None or self.vertex_y is None or self.start is None or self.end is None:
            raise ValueError("Vertex, start, and end points must be set for 'Parabola' process.")

        x0, y0 = self.vertex_x, self.vertex_y
        x1, y1 = self.start
        x2, y2 = self.end

        # Система уравнений для a, b, c, используя точку вершины и две другие точки
        A = np.array([[x1**2, x1, 1], [x2**2, x2, 1], [x0**2, x0, 1]])
        B = np.array([y1, y2, y0])
        self.a, self.b, self.c = np.linalg.solve(A, B)

    def plot(self, ax, config):
        self.calculate_coefficients()

        ## Ensure end_y_or_type is specified
        # if isinstance(self.end, tuple) and isinstance(self.end[1], str):
        # end_x, end_y_or_type = self.end
        # if end_y_or_type == 'x':
        # x2 = end_x
        # y2 = self.a * self.x2**2 + self.b * self.x2 + self.c
        # elif end_y_or_type == 'y':
        # y2 = end_y
        # x2 = (-self.b + np.sqrt(self.b**2-4*self.a*self.c)) / (2*self.a)
        ## x2=(-self.b - np.sqrt(self.b**2-4*self.a*self.c)) / (2*self.a)
        # self.end = (x2, y2)

        print(self.a, self.b, self.c)
        if self.start and self.end:
            x1, y1 = self.start
            x2, y2 = self.end
            self.x_values = np.linspace(x1, x2, 100)
            self.y_values = self.a * self.x_values**2 + self.b * self.x_values + self.c
            super().plot(ax, config)


# def end_x(process):
# if process.type == 'power':
# x1, y1 = process.start
# _, y2 = process.end
# return x1 * (y2 / y1)**0.5
# def end_y(process):
# if process.type == 'power':
# x1, y1 = process.start
# x2, _ = process.end
# return y1 * (x2 / x1)**2

# end_p, end_V are not needed:
# Use
# A1 = Adiabatic().to(v1,'volume')
# v1 = A1.end[0]
# p1 = A1.end[1]

# def end_v(process):
# V1, p1 = process.start
# if process.type == 'iso_t':
# _, p2 = process.end
# return V1 * p1 / p2
# elif process.type == 'adiabatic':
# _, p2 = process.end
# return V1 * (p1 / p2) ** (1 / process.gamma)
# return None
# def end_p(process):
# V1, p1 = process.start
# if process.type == 'iso_t':
# V2, _ = process.end
# return p1 * V1 / V2
# elif process.type == 'adiabatic':
# V2, _ = process.end
# return (p1 * V1 ** process.gamma) / V2 ** process.gamma
# return None


# Find intersection adiabatic and iso_t using (v1,p1) and (v3,p3)
def common_pv(v1, p1, v3, p3, gamma=5 / 3):
    v2 = v1 ** (gamma / (gamma - 1)) * (p1 / (p3 * v3)) ** (1 / (gamma - 1))
    p2 = p3 * v3 / v2
    return v2, p2


# Find intersection adiabatic and iso_t using process names
def common_QT(process1, process2, gamma=5 / 3):
    if process1.type == 'state':
        x1, y1 = process1.start
    else:
        x1, y1 = process1.end
    if process2.type == 'state':
        x2, y2 = process2.start
    else:
        x2, y2 = process2.end
    ### Calculate common x, y
    x = (y1 * x1**gamma / (y2 * x2)) ** (1 / (gamma - 1))
    y = y2 * x2 / x
    return x, y


# Distribute points evenly along the curve for better arrow placement
def interpolate_curve(x_values, y_values, num_points=100):
    # Calculate the curve length
    total_length = np.sum(np.sqrt(np.diff(x_values) ** 2 + np.diff(y_values) ** 2))
    length_along_curve = np.insert(np.cumsum(np.sqrt(np.diff(x_values) ** 2 + np.diff(y_values) ** 2)), 0, 0)

    # Limit the maximum distance by the maximum value of the curve length
    max_length = length_along_curve[-1]
    distance = np.linspace(0, max_length, num_points)

    # Interpolate x and y as functions of length
    f_x = interp1d(length_along_curve, x_values, kind='linear', bounds_error=False, fill_value='extrapolate')
    f_y = interp1d(length_along_curve, y_values, kind='linear', bounds_error=False, fill_value='extrapolate')

    # Calculate new x and y values
    new_x_values = f_x(distance)
    new_y_values = f_y(distance)

    return new_x_values, new_y_values
