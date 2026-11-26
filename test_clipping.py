from io import BytesIO
import unittest
from unittest.mock import patch

import matplotlib
import numpy as np
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.image import imread

from . import Drawing, Linear


class CurveClippingTest(unittest.TestCase):
    def test_edge_strokes_and_crossings(self):
        with matplotlib.rc_context(), patch('matplotlib.pyplot.show'), Drawing() as d:
            d.set_config(xlim=(0, 10), ylim=(0, 10), xaxis=False, yaxis=False,
                         zero=True, zero_x=1, xname=None, yname=None)
            d.fig.set_dpi(144)
            canvas = FigureCanvasAgg(d.fig)
            d.ax.set_xticks([2, 4])
            # The right end of this same polyline crosses the bottom edge.
            d.ax.plot([2, 6, 8, 8], [0, 0, 2, -2], color='black', lw=6)
            Linear().at(2, 10).to(6, 10).lw(8)
            d.ax.vlines([0, 10], 3, 5, lw=[7, 9], colors='black')
            Linear().at(0, 2).to(2, 3).lw(12)
            Linear().at(-1, 8).to(1, 8).lw(4).clip(False)
            d.show()
            canvas.draw()
            ink = 1 - np.asarray(canvas.buffer_rgba())[:, :, 0] / 255

            def sample(x, y):
                col, row = np.rint(d.ax.transData.transform((x, y))).astype(int)
                return ink[ink.shape[0] - row - 15:ink.shape[0] - row + 15, col - 15:col + 15]

            for pos, width, axis in [((3, 0), 6, 0), ((4, 10), 8, 0),
                                     ((0, 4), 7, 1), ((10, 4), 9, 1)]:
                with self.subTest(pos=pos):
                    self.assertAlmostEqual(np.median(sample(*pos).sum(axis)), width * 2, delta=1)
            self.assertLess(sample(8, -0.1)[15, 15], 0.05)
            self.assertLess(sample(-0.1, 2)[15, 15], 0.05)
            self.assertGreater(sample(-0.3, 8)[15, 15], 0.95)

    def test_tight_save_keeps_outer_half_stroke(self):
        with matplotlib.rc_context(), patch('matplotlib.pyplot.show'), Drawing() as d:
            d.set_config(xlim=(0, 10), ylim=(0, 10), xaxis=False, yaxis=False,
                         zero=False, xname=None, yname=None)
            d.ax.set_axis_off()
            d.ax.hlines([0, 10], 2, 8, lw=8, colors='black')
            d.show()
            output = BytesIO()
            d.save(output, format='png', dpi=144)
            output.seek(0)
            ink = 1 - imread(output, format='png')[:, :, 0]
            column = ink[:, ink.shape[1] // 2]
            for edge in [column[:30], column[-30:]]:
                self.assertAlmostEqual(edge.sum(), 16, delta=1)
