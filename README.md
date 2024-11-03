`plotnik` is a Python library designed for creating simple graphs using
matplotlib in Cartesian coordinates, mirroring the style of 'school' graphs
traditionally used in Russian physics and mathematics education. It was
developed for convenient drawing of thermodynamic cycles, including nonlinear
processes, without need to perform calculations.

The library is currently usable. The code is poorly designed.
Full documentation is not available, but you can refer to the examples
provided below to understand its functionality.

The library utilizes syntax inspired by the
[SchemDraw](https://github.com/cdelker/schemdraw) library.

The code has been mostly written by Chat-GPT.

## Basic usage

The default font is 'STIX Two Text'. To switch to Computer Modern Roman, use
`d.set_config(font='serif')`, noting that this requires LaTeX to be installed
on your machine.

To draw the curves, use `processes`: class `Process()` with its subclasses:

- `Linear()`
  Draw a straight line from .at() to .to().

- `Power()`
  Connects initial and final points with the equation y=k*x^n + b

- `Adiabatic()`
  Draw adiabatic process pV^gamma = const for p(V) coordinates.
  Set the gamma value using `Adiabatic(gamma=7/5)`, with the default being 5/3.
  
- `Iso_t()`
  Isothermal process pV=const in p(V) coordinates.

- `Bezier(x,y)`
  Draw quadratic or cubic Bezier curve.

      d += Bezier(x=2,y=2).at(1,1).to(3,1)

  draws quadratic Bezier curve from (1,1) to (3,1) with a single control point
  at (2,2). Similarly,

      d += Bezier(x1=3,y1=7, x2=5,y2=3).at(1,5).to(7,5)

  this code plots a cubic Bezier curve, resembling a sine wave, with two
  control points at (x1, y1) and (x2, y2). Note that `d +=` is *usually* optional.

Additionally, standard matplotlib syntax can be used to add text and lines to
the plot, for example, `d.ax.plot(x, y)`.


## Examples
### 1. V=const, adiabatic, isothermal
This example illustrates well the purpose behind the creation of the library.
It is necessary to draw a cycle in pV-coordinates, consisting of an isochore,
adiabat, and isotherm. The goal was to free the user from the need to perform
calculations and to provide a simple interface for constructing such graphs.

``` python
from plotnik import *

v1 = 3
v2 = 9
v3 = v1

p1 = 9

with Drawing() as d:
    d.set_config(
        xname='$V$',
        yname='$p$',
        zero_x=0.5,
        axes_arrow_width=0.23,
    )

    A1 = Adiabatic().at(v1,p1).to(v2, 'volume').arrow().dot()
    p2 = A1.end[1] # A1.end returns coordinates (x,y) for the last point of A1 process

    # Process T1 has no .at(), so it takes the last point from the previous
    # process A1 as an initial point
    T1 = Iso_t().to(v1, 'volume').arrow().dot().label(2, dy=0)
    p3 = T1.end[1]

    Linear().to(v1,p1).arrow().dot().label(3,1)

    d.show()
    # `crop=True` is only compatible with SVG files and requires the installation of `Inkscape` on your machine.
    # This feature removes paths named `patch_1` and `patch_2`, which, in my case, do not contain any paths
    # but add a whitespace margin.
    d.save('filename.svg', crop=True)

```
<img width="400" src="https://github.com/pozitron57/plotnik/assets/9392655/04720dfd-a606-4039-86be-5c3a46e6f1b1">

### 2. Linear() and grid()
``` python
from plotnik import *

u1 = 2
u2 = 4

v1 = 3
v2 = 6

with Drawing() as d:
    d.set_config(
        yname='$U$',
        xname='$V$',
        zero_x=0.4,
        ylim=[0,6],
        xlim=[0,8],
    )

    Linear().at(v1,u1).to(v2,u2).arrow().dot('both').label(1,2)
    d.grid(y_end=5)
    d.show()
```
<img width="400" src="https://github.com/pozitron57/plotnik/assets/9392655/673919fa-3dd1-4c92-997e-acf23d9e8c40">

### 3. Carnot cycle in PV coordinates. Adiabatic(), Iso_t().
``` python
from plotnik import *

p1 = 10
v1 = 3
v2 = 6
v3 = 10

with Drawing() as d:
    d.set_config(
        fontsize=30,
        yname='$p$',
        xname='$V$',
        aspect=0.7,
        xlim=[0,11],
        center=[5.5, 4.5],
    )

    # When the second argument in the .to() method is 'volume', the function draws a line up to
    # volume v2 and calculates the required pressure. To retrieve this pressure value, use end_p(process)
    T1 = Iso_t().at(v1, p1).to(v2, 'volume').dot('both').label(1,2)
    p2 = T1.end[1]

    A1 = Adiabatic().to(v3, 'volume')
    p3 = A1.end[1]

    # common_pv calculates the volume (v) and pressure (p) at the intersection of an isothermal process
    # passing through the start point and an adiabatic process passing through the end point.
    v4, p4 = common_pv(v1,p1, v3,p3)
    Iso_t().to(v4, 'volume').dot('both').label(3,4)

    Adiabatic().to(v1,'volume')
    Power(15).at(v2, p2).to(v4,p4)

    d.ax.text(4.75, 4.8, '$A_1$', fontsize=24)
    d.ax.text(5.65, 3.9, '$A_2$', fontsize=24)

    d.show()
```
<img width="400" src="https://github.com/pozitron57/plotnik/assets/9392655/cf1f0a52-f2e7-4e6a-9006-947515c56170">

### 4. Cubic Bezier curve with dots on it
``` python
from plotnik import *

with Drawing() as d:
    d.set_config(yname=r'$x$',
                 xname=r'$t$',
                 xlim=[0,12],
                 center_x=5,
                 )

    B = Bezier(x1=5,y1=15, x2=6.8,y2=-4).at(1,7).to(11,3).lw(2.4)

    # B.get_point(index) returns a tuple (x, y).
    # Use an asterisk to unpack this tuple into x and y.
    # The allowed index range is from 0 to 100. 
    State().at(*B.get_point( 4)).dot().label('A')
    State().at(*B.get_point(18)).dot().label('B', dx=0)
    State().at(*B.get_point(48)).dot().label('C')
    State().at(*B.get_point(91)).dot().label('D')

    d.show()
```
<img width="400" src="https://github.com/pozitron57/plotnik/assets/9392655/b08c31dd-6b02-460d-ae2b-830bc6cfa392">

### 5. Power() to create shifted hyperbola y=k/x+b
```python
from plotnik import *

x1 = 3
y1 = 2

x2 = 2*x1
y2 = y1

x3 = x1
y3 = 3*y1

with Drawing() as d:
    d.set_config(
        fontsize=31,
        yname='$p$',
        xname=r'$\rho$',
        xlim=[0,7.5],
        ylim=[0,7.5],
        axes_arrow_width=0.16,
        zero_x=0.4, # add zero as a xtick label shifted to x=-0.4
        )

    Linear().at(x1, y1).to(x2,y2).arrow().dot().tox().label(1,2, dy=-0.65)
    Power(power=-0.5).at(x2, y2).to(x3, y3).arrow().label('',3)
    Linear().to(x1,y1).arrow().dot('both').toy()

    d.ax.set_yticks([y1, y3], ['$p_0$', '$3p_0$'])
    d.ax.set_xticks([x1, x2], [r'$\rho_0$', r'$2\rho_0$'])

    d.show()
```
<img width="400" src="https://github.com/pozitron57/plotnik/assets/9392655/d59e376e-0ef6-4f9e-a02a-cda4878efd36">

### 6. Two Adiabatic() & two Linear()
``` python
from plotnik import *

v1  = 2
v2  = 5
p12 = 8
p34 = 3

with Drawing() as d:
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
    Linear().at(v1,p12).to(v2,p12).dot('both').arrow(size=a,pos=0.61).label(1,2)
    Q1 = Adiabatic().at(v1,p12).to(p34, 'pressure').arrow(size=a,reverse=True)
    Q2 = Adiabatic().at(v2,p12).to(p34, 'pressure').arrow(size=a)
    v3 = Q1.end[0]
    v4 = Q2.end[0]
    Linear().at(v4,p34).to(v3,p34).dot('both').arrow(size=a).label(3,4, dy=-0.8)

    d.show()
```
<img width="400" src="https://github.com/pozitron57/plotnik/assets/9392655/bcaacd65-30f0-411d-96f7-f1f0989c0fa1">

### 7. Bezier().connect() method

This method is used to create a smooth curve that must pass through the specified point,
in this case, (3,60).

``` python
from plotnik import *

with Drawing() as d:
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
    d += (L1:= Linear().at(5,90).to(6,90).lw(0) ) # This process is used solely to complete the Bezier curve with a tangent, hence 'lw=0' is specified.
    Bezier().connect(P1,L1).lw(3)

    d.ax.set_xticks([2,4])
    d.ax.set_yticks([40,80])
        
    d.grid(step_x=0.5, step_y=10, x_end=5, y_end=90)

    d.show()
```
<img width="400" src="https://github.com/pozitron57/plotnik/assets/9392655/0ff9d3d2-fc7b-4fcb-8579-59f208db8560">

### 8. Bezier().get_coordinates()
When plotting a complex curve as two separate processes (thus requiring two calls to `ax.plot()`),
using a large linewidth may result in poor connections between the segments.
To resolve this, you can use `Bezier()` to calculate the coordinates without plotting them.
Then, append these coordinates to the other process.
Matplotlib will seamlessly join these segments when plotting them in a single `ax.plot()` call.

``` python
from plotnik import *

with Drawing() as d:
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
<img width="500" src="https://github.com/pozitron57/plotnik/assets/9392655/2ea4db27-f302-46bf-8e78-2f568297990e">

### 9. Power()
``` python
from plotnik import *

v1 = 8
u1 = 6
v2 = 3.5

with Drawing() as d:
    d.set_config(
        fontsize=31,
        yname='$U$', 
        xname='$V$',
        ylim=[0,7.4],
        axes_arrow_length=1.1,
        center=[10,0],
    )

    P1 = Power().at(v1, u1).to(v2, 'x').arrow().label(1,2).dot('both').tox().toy()
    y2 = P1.end[1]

    Power().to(0, 0).ls('--')

    d.ax.set_xticks([v1, v2], ['$V_1$', '$V_2$'])
    d.ax.set_yticks([u1, y2], ['$U_1$', '$U_2$'])

    d.show()
```
<img width="400" src="https://github.com/pozitron57/plotnik/assets/9392655/6f3aa682-4f9e-4b08-b426-9cba5448a094">

### 10. Arrows and labels positioning
``` python
from plotnik import *

v1 = 2
v2 = v1
v3 = 6
v4 = v3

t1 = 4
t2 = 2
t3 = 6
t4 = 8

with Drawing() as d:
    d.set_config(
        yname='$V$',
        lw=3.2,
        xname='$T$',
        ylim=[0,7],
        xlim=[0,10],
        zero_x=0.5,
        axes_arrow_scale=1.5,
    )

    Linear().at(t1, v1).to(t2, v2).arrow().dot('both').tox()\
       .label(1,2, start_ofst=[0.5,0.2], end_ofst=[-0.8, 0.2])
    Linear().to(t3, v3).arrow().tozero('start')
    Linear().to(t4, v4).arrow(pos=0.7).tox().dot('both')\
       .label(3,4, start_dx=-0.5)

    d.ax.set_xticks([2,4,6,8], ['$T_0$','$2T_0$','$3T_0$','$4T_0$'])

    d.show()
```
<img width="400" src="https://github.com/pozitron57/plotnik/assets/9392655/4811a843-8bc3-48b1-947f-01900578dd3d">

### 11. Customize grid()
``` python
from plotnik import *

B = [0, 0.2, 0]
t = [0, 2,   4]

with Drawing() as d:
    d.set_config(yname='$B,$Тл', xname='$t,$с',
                 xlim=[0,6.3],
                 xname_x=5,
                 yname_y=0.26,
                 ylim=[0,0.27],
                 zero_x=0.3,
                 axes_arrow_scale=1.5,
                 aspect=20,
                 )

    d.ax.plot(t,B,'k-', lw=2.5)

    d.ax.set_yticks([0.1,0.2], ['0,1','0,2'])
    d.ax.set_xticks([1,2,3,4])

    d.grid(step_x=1, step_y=0.05, x_end=4.2, y_end=0.21, lw=2, color='#333333')

    d.show()
```
<img width="400" src="https://github.com/pozitron57/plotnik/assets/9392655/6d77acc6-2835-4116-8c9a-dc019ee9b72a">

### 12. Tangent red isotherm
``` python
from plotnik import *

p1=3
v1=1
p2=1
v2=4
a = (p1-p2) / (v1-v2)
b = p1 - a*v1
vm = -b/(2*a)
pm = a*vm + b

with Drawing() as d:
    d.set_config(
        fontsize=24,
        yname='$p$',
        xname='$V$',
        xlim=[0,5],
        ylim=[0,4],
        zero_ofst=[0.2, 0.38],
    )

    Linear().at(v1,p1).to(v2,p2).arrow(pos=0.3).dot('both').label(1,2).toy().tox()
    State().at(vm,pm).dot().tox().toy()
    Iso_t().at(vm,pm).to(v1*1.35,'volume').lw(1.4).col('#EE3344')
    Iso_t().at(vm,pm).to(v2*1.16,'volume').lw(1.4).col('#EE3344')

    d.ax.set_yticks([p1, p2, pm], ['$p_1$', '$p_2$', r'$p_\text{м}$'])
    d.ax.set_xticks([v1, v2, vm], ['$V_1$', '$V_2$', r'$V\!_\text{м}$'])

    d.grid(step=.5, y_end=3.5, x_end=4.5, color='#dddddd')

    d.show()
```
<img width=450 src=https://github.com/pozitron57/plotnik/assets/9392655/169d68fa-bcef-417d-ba43-a009e3cb907d>

## Some options
Consider the followig syntax:

`Linear().at().to().arrow().dot().label().toy().tox().tozero().col().lw().ls().zord()`.

`.at(x1,y1)`: set starting point. Uses previous process last point if not set.

`.to(x2,y2)`: set end point.

`.arrow(size=None, pos=0.54, color='black', reverse=False,
              filled=True, zorder=3, head_length=0.6,
              head_width=0.2)`

  - `pos` sets position of the arrow on the line (from 0 to 1).
  - `reverse=True` rotates the arrow on 180 degrees.
  - `filled=False` doesn't look well but produces not filled arrow.

`.dot(pos='end', size=8, color='black', zorder=5, marker='o')`
  - `.dot()` or `.dot('end')` or `.dot(pos='end')` adds only last point;
  - `.dot('start')` adds only start point;
  - `.dot('both')` adds two points.
  - `.dot(size=25)`
  - `marker` are standart matplotlib markers, see
    [full list](https://matplotlib.org/stable/api/markers_api.html)
  - `zorder` can change the order it appears relative to other elements
    (useful to plot marker above or below grid or process etc.).

`.label()` add 1 or two labels.

`.tox(), .toy(), .tozero()` draw lines to, correspondingly, horizontal axis,
vertical axis and zero. Default linestyle is dashed line, can be changed like
`.tox(ls='-')`. By default, draw lines both for start and end of the process.
Can be changed like `.tox('end')` or `.tox('start')`.

`.col('red')` set color for the line.

`.lw(1)` set linewidth for the process.

`.ls('--')` set linestyle for the process.

`.zord(5)` set zorder for the process.



## TODO

- Repair examples 7 and 8 so `d +=` won't be required.

- Revise the arrow positioning logic to ensure they are accurately centered.

- In the `set_config()` function, add the capability to globally modify arrowsize,
  dotsize, and lw (line width) for processes.

  Introduce options in the `set_config()` to globally adjust the size of arrows,
  dots, and line width for processes. For instance,
  include settings like `dots_all=True`, `dots_size=10` and `arrows_all=True`,
  `arrows_size=23`.

- Integrate the feature to select different coordinates. For instance, if all
processes are initially plotted in x, y coordinates, there should be an option
to view them in transformed coordinates like 1/x, y^2. Example syntax could be:
`d.transform_coordinates(newx = 1/x, newy = y**2)`.

- Address the issue where `d.save()` generates erroneous results when used without
a prior call to `d.show()`, ensuring reliable save functionality.

- `.xtick()` and `d.add_xticks()` use different codes for tick positioning.

- make `.xtick()` use matplotlib `ax.set_xticks()` method

- Improve the algorithm for automatic determination of positions and sizes for
labels, ticks, and arrows.

- When need `Bezier()` only to calculate coordinates, you have to add it to
  `Drawing()` like so:

      d += (B1:= Bezier(x=1.8,y=2.8).at(1, 10).to(4, 2.5).lw(0) )
      x,y = B1.get_coordinates()

  Rewrite the code so one can use
  
      B1 = Bezier(x=1.8,y=2.8).at(1, 10).to(4, 2.5).hide()
      x,y = B1.get_coordinates()

  without adding it an actual figure.
