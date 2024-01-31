Plotnik is a library for creating simple graphs using matplotlib in Cartesian
coordinates in the style of 'school' graphs used in physics and mathematics
problems. It allows for drawing thermodynamic cycles, including nonlinear
processes.

The library is already usable but in an early stage of development.

The library utilizes syntax inspired by the
[SchemDraw](https://github.com/cdelker/schemdraw) library.

The code is written almost entirely by Chat-GPT.

## Examples

``` python
import plotnik
from plotnik.processes import *

v1 = 8
u1 = 6
v2 = 3.5

with plotnik.Drawing() as d:
    d.set_config(
        fontsize=31,
        yname='$U$', 
        xname='$V$',
        ylim=[0,7.4],
        axes_arrow_length=1.1,
        center=[10,0],
    )

    d += (P1:= Power().at(v1, u1).to(v2, 'x').arrow().label(1,2).dot('both').tox().toy() )
    y2 = end_y(P1)

    d += Power().at(v2, y2).to(0, 0).ls('--')

    d.ax.set_xticks([v1, v2], ['$V_1$', '$V_2$'])
    d.ax.set_yticks([u1, y2], ['$U_1$', '$U_2$'])

    d.show()
```


## TODO

- Revise the arrow positioning logic to ensure they are accurately centered.

- In the set_config function, add the capability to globally modify arrowsize,
  dotsize, and lw (line width) for processes.

  Introduce options in the set_config() to globally adjust the size of arrows,
  dots, and line width for processes. For instance,
  include settings like `dots_all=True`, `dots_size=10` and `arrows_all=True`,
  `arrows_size=23`. 

- Integrate the feature to select different coordinates. For instance, if all
processes are initially plotted in x, y coordinates, there should be an option
to view them in transformed coordinates like 1/x, y^2. Example syntax could be:
d.transform_coordinates(newx = 1/x, newy = y\**2).

- Address the issue where d.save() generates erroneous results when used without
a prior call to d.show(), ensuring reliable save functionality.

- .xtick() and d.add_xticks() use different codes for tick positioning.

- make .xtick() use matplotlib ax.set_xticks() method

- Improve the algorithm for automatic determination of positions and sizes for
labels, ticks, and arrows. 
