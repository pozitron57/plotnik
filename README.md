Plotnik is a library for creating simple graphs using matplotlib in Cartesian
coordinates in the style of 'school' graphs used in physics and mathematics
problems. It allows for drawing thermodynamic cycles, including nonlinear
processes.

The library is already usable but in an early stage of development.
No documentation is available, but you may use some examples below to get the idea.
You may use `processes`, namely
`Linear()`,
`Power()`,
`Adiabatic()`,
`Iso_t()`,
`Bezier()`.

Otherwise, you can also use standard matplotlib syntax to add text and lines to the plot.

The library utilizes syntax inspired by the
[SchemDraw](https://github.com/cdelker/schemdraw) library.

The code is written almost entirely by Chat-GPT.

## Examples
### 1
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

    d += Power().to(0, 0).ls('--')

    d.ax.set_xticks([v1, v2], ['$V_1$', '$V_2$'])
    d.ax.set_yticks([u1, y2], ['$U_1$', '$U_2$'])

    d.show()
```

![image](https://github.com/pozitron57/plotnik/assets/9392655/6f3aa682-4f9e-4b08-b426-9cba5448a094)

### 2
``` python
import plotnik
from plotnik.processes import *

u1 = 2
u2 = 4

v1 = 3
v2 = 6

with plotnik.Drawing() as d:
    d.set_config(
        yname='$U$',
        xname='$V$',
        zero_x=0.4,
        ylim=[0,6],
        xlim=[0,8],
    )

    d += Linear().at(v1,u1).to(v2,u2).arrow().dot('both').label(1,2)
    d.grid(y_end=5)
    d.show()
```
![image](https://github.com/pozitron57/plotnik/assets/9392655/673919fa-3dd1-4c92-997e-acf23d9e8c40)

### 3 (Carnot cycle in PV coordinates)

import plotnik
from plotnik.processes import *

p1 = 10
v1 = 3
v2 = 6
v3 = 10

``` python
with plotnik.Drawing() as d:
    d.set_config(
        fontsize=30,
        yname='$p$',
        xname='$V$',
        aspect=0.7,
        xlim=[0,11],
        center=[5.5, 4.5],
    )
                 
    d += (T1:= Iso_t().at(v1, p1).to(v2, 'volume').dot('both').label(1,2) )

    d += (Q1:= Adiabatic().to(v3, 'volume') )
    p3 = end_p(Q1)

    v4, p4 = common_pv(v1,p1, v3,p3)
    d += Iso_t().to(v4, 'volume').dot('both').label(3,4)

    d += Adiabatic().to(v1,p1)
    d += Power(15).at(v2, end_p(T1)).to(v4,p4)

    d.ax.text(4.75, 4.8, '$A_1$', fontsize=24)
    d.ax.text(5.65, 3.9, '$A_2$', fontsize=24)

    d.show()
```
![image](https://github.com/pozitron57/plotnik/assets/9392655/cf1f0a52-f2e7-4e6a-9006-947515c56170)



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
