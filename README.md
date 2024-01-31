`plotnik` is a Python library for creating simple graphs using `matplotlib` in Cartesian
coordinates in the style of 'school' graphs used in Russian tradition in physics and mathematics
problems. It was developed for convenient drawing thermodynamic cycles, including nonlinear
processes.

The library is already usable but in an early stage of development.
No full documentation is available, but you may use some examples below to get
the idea.

The library utilizes syntax inspired by the
[SchemDraw](https://github.com/cdelker/schemdraw) library.

The code is written almost entirely by Chat-GPT.

## Basic usage

``` python
import plotnik
from plotnik.processes import *

with plotnik.Drawing() as d:
    d.set_config() # Set options
    d += Linear().at(1, 1).to(2, 2).arrow().label(1,2).dot('both').tox().toy()
    d += Power(0.5).to(3, 3) # takes 2,2 as initial point from previous process
    d.show()
    d.save('filename')

```

Standard font is "STIX Two Text". Use `d.set_config(font='serif')` to get computer modern roman (need latex to be installed on your machine).

To draw the lines, you may use `processes`: class `Process()` with its subclasses:

- `Linear()`
  Draw a straight line from .at() to .to().

- `Power()`
  Connect initial and last points with y=k*x\**n + b

- `Adiabatic()`
  Draw adiabatic process pV^gamma = const for p(V) coordinates.
  Set gamma: Adiabatic(gamma=7/5) (default value is 5/3).

- `Iso_t()`
  Isothermal process pV=const in p(V) coordinates.

- `Bezier(x,y)`
  Draw quadratic or cubic Bezier curve.

      d += Bezier(x=2,y=2).at(1,1).to(3,1)

  draws quadratic Bezier curve from (1,1) to (3,1) with a single control point at (2,2).
  Similarly,

      d += Bezier(x1=3,y1=7, x2=5,y2=3).at(1,5).to(7,5)
    
  plots a cubic Bezier curve (sine-like) with two control points (x1,y1) and (x2,y2).

Otherwise, you can also use standard matplotlib syntax to add text and lines to
the plot, such as `d.ax.plot(x,y)`.


## Examples
### 1. Power()
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

### 2. Linear() and grid()
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

### 3. Carnot cycle in PV coordinates. Adiabatic(), Iso_t().
``` python
import plotnik
from plotnik.processes import *

p1 = 10
v1 = 3
v2 = 6
v3 = 10

with plotnik.Drawing() as d:
    d.set_config(
        fontsize=30,
        yname='$p$',
        xname='$V$',
        aspect=0.7,
        xlim=[0,11],
        center=[5.5, 4.5],
    )

    # When second argument in .to() is 'volume', it draws a line until volume v2 and calculate
    # needed pressure for that. Then use end_p(process) to get this pressure value.
    d += (T1:= Iso_t().at(v1, p1).to(v2, 'volume').dot('both').label(1,2) )
    p2 = end_p(T1)

    d += (Q1:= Adiabatic().to(v3, 'volume') )
    p3 = end_p(Q1)

    # common_pv calculates v,p where isothermal through the start point and adiabatic process throught the
    # end point crosses
    v4, p4 = common_pv(v1,p1, v3,p3)
    d += Iso_t().to(v4, 'volume').dot('both').label(3,4)

    d += Adiabatic().to(v1,p1)
    d += Power(15).at(v2, p2).to(v4,p4)

    d.ax.text(4.75, 4.8, '$A_1$', fontsize=24)
    d.ax.text(5.65, 3.9, '$A_2$', fontsize=24)

    d.show()
```
![image](https://github.com/pozitron57/plotnik/assets/9392655/cf1f0a52-f2e7-4e6a-9006-947515c56170)

### 4. Cubic Bezier curve with dots on it
``` python
import plotnik
from plotnik.processes import *

with plotnik.Drawing() as d:
    d.set_config(yname=r'$x$',
                 xname=r'$t$',
                 xlim=[0,12],
                 center_x=5,
                 )

    d += (B:= Bezier(x1=5,y1=15, x2=6.8,y2=-4).at(1,7).to(11,3).lw(2.4) )

    # B.get_point(index) returns (x,y). Use an asterisk to unpack it to x,y.
    # Allowed indices are from 0 to 100
    d += State().at(*B.get_point( 4)).dot().label('A')
    d += State().at(*B.get_point(18)).dot().label('B', start_dx=0)
    d += State().at(*B.get_point(48)).dot().label('C')
    d += State().at(*B.get_point(91)).dot().label('D')

    d.show()
```

![image](https://github.com/pozitron57/plotnik/assets/9392655/b08c31dd-6b02-460d-ae2b-830bc6cfa392)

### 5. Power() to create shifted hyperbola y=k/x+b
```python
import plotnik
from plotnik.processes import *

x1 = 3
y1 = 2

x2 = 2*x1
y2 = y1

x3 = x1
y3 = 3*y1

with plotnik.Drawing() as d:
    d.set_config(
        fontsize=31,
        yname='$p$',
        xname=r'$\rho$',
        xlim=[0,7.5],
        ylim=[0,7.5],
        axes_arrow_width=0.16,
        zero_x=0.4, # add zero as a xtick label shifted to x=-0.4
        )

    d += Linear().at(x1, y1).to(x2,y2).arrow().dot().tox().label(1,2, dy=-0.65)
    d += Power(power=-0.5).at(x2, y2).to(x3, y3).arrow().label('',3)
    d += Linear().to(x1,y1).arrow().dot('both').toy()

    d.ax.set_yticks([y1, y3], ['$p_0$', '$3p_0$'])
    d.ax.set_xticks([x1, x2], [r'$\rho_0$', r'$2\rho_0$'])

    d.show()
```
![image](https://github.com/pozitron57/plotnik/assets/9392655/d59e376e-0ef6-4f9e-a02a-cda4878efd36)

### 7. Two Adiabatic() & two Linear()
``` python
import plotnik
from plotnik.processes import *

v1  = 2
v2  = 5
p12 = 8
p34 = 3

with plotnik.Drawing() as d:
    d.set_config(
         yname='$p$',
         xname='$V$',
         zero_x=0.5,
         fontsize=28,
         ylim=[0,10.7],
         axes_arrow_scale=0.7,
         center_x=4,
     )

    a=22
    d += Linear().at(v1,p12).to(v2,p12).dot('both').arrow(size=a,pos=0.61).label(1,2)
    d += (Q1:= Adiabatic().at(v1,p12).to(p34, 'pressure').arrow(size=a,reverse=True) )
    d += (Q2:= Adiabatic().at(v2,p12).to(p34, 'pressure').arrow(size=a) )
    v3 = end_v(Q1)
    v4 = end_v(Q2)
    d += Linear().at(v4,p34).to(v3,p34).dot('both').arrow(size=a)\
             .label(3,4, dy=-0.8)

    d.show()
```

![image](https://github.com/pozitron57/plotnik/assets/9392655/bcaacd65-30f0-411d-96f7-f1f0989c0fa1)

### 8. Bezier().connect() method
Reproduce a smooth curve that has to pass through the point (3,60).

``` python
import plotnik
from plotnik.processes import *

with plotnik.Drawing() as d:
    d.set_config(
        aspect=1/20,
        yname=r'$\alpha, \%$',
        yname_y=103,
        xname=r'$T,10^3 \rm{К}$',
        xlim=[0,6],
        ylim=[0,106],
        zero_ofst=[0.2, 11.8]
    )

    d += (P1:= Power(2).at(0,0).to(3,60).lw(3) )
    d += (L1:= Linear().at(5,90).to(6,90).lw(0) ) # process needed only to finish Bezier as a tangent to it hence lw=0
    d += Bezier().connect(P1,L1).lw(3)

    d.ax.set_xticks([2,4])
    d.ax.set_yticks([40,80])
        
    d.grid(step_x=0.5, step_y=10, x_end=5, y_end=90)

    d.show()
```
![image](https://github.com/pozitron57/plotnik/assets/9392655/0ff9d3d2-fc7b-4fcb-8579-59f208db8560)

### 9. Bezier().get_coordinates()
when plot a complex curve as two separate processes (hence two calls of `ax.plot()`)
with large linewidth there may be a bad connection between it. To avoid it, you can use Bezier() to
calculate coordinates without plotting it. Then append these coordinates to other process
and matplotlib will smooth it.

``` python
import plotnik
from plotnik.processes import *

with plotnik.Drawing() as d:
    d.set_config(
        yname=r'$V_{\rm погр},\rm{см}^3$',
        xname=r'$\rho,\rm{г}/\rm{см}^3$',
        ylim=[0,12],
        xlim=[0,4.8],
        aspect=1/4,
        fontsize=18,
        axes_arrow_width=0.2,
        )

    d += (B1:= Bezier(x=1.8,y=2.8).at(1, 10).to(4, 2.5).lw(0) )
    x,y = B1.get_coordinates()
    # Append straight line to x,y
    x = np.append([0,1],x)
    y = np.append([10,10],y)

    d.ax.plot(x, y, lw=2.5, color='k')

    d.ax.tick_params(length=0)
    d.ax.set_yticks(np.arange(1,11,1))
    d.ax.set_xticks(np.arange(0.5,4.5,0.5),
                    ['0,5','1,0','1,5','2,0','2,5','3,0','3,5','4,0'])
    d.grid(step_x=0.25, step_y=1, y_end=10, x_end=4)

    d.show()
```
![image](https://github.com/pozitron57/plotnik/assets/9392655/2ea4db27-f302-46bf-8e78-2f568297990e)

### 10. V=const, adiabatic, isothermal
``` python
import plotnik
from plotnik.processes import *

v1 = 3
v2 = 9
v3 = v1

p1 = 9


with plotnik.Drawing() as d:
    d.set_config(
        xname='$V$',
        yname='$p$',
        zero_x=0.5,
        axes_arrow_width=0.23,
    )

    d += (Q1 := Adiabatic().at(v1,p1).to(v2, 'volume').arrow().dot() )
    p2 = end_p(Q1)

    d += (T1 := Iso_t().at(v2,p2).to(v1, 'volume').arrow().dot().label(2, dy=0) )
    p3 = end_p(T1)

    d += Linear().at(v3,p3).to(v1,p1).arrow().dot().label(3,1)

    d.show()

```
![image](https://github.com/pozitron57/plotnik/assets/9392655/04720dfd-a606-4039-86be-5c3a46e6f1b1)


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
