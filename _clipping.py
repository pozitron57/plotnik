"""Clip curves at the data limits while preserving strokes that follow a limit."""

import numpy as np
from matplotlib.collections import LineCollection
from matplotlib.lines import Line2D
from matplotlib.patches import Patch, Rectangle
from matplotlib.path import Path
from matplotlib.transforms import Bbox, BboxTransformTo, IdentityTransform


def _strokes(artist):
    if isinstance(artist, Line2D) and artist.get_linestyle() != 'None':
        yield artist.get_path(), artist.get_linewidth()
    elif isinstance(artist, LineCollection):
        # hlines/vlines and ordinary polylines use a shared data transform.
        # Offset or individually transformed collections keep their usual clip.
        if np.any(artist.get_offsets()) or len(artist.get_transforms()):
            return
        widths = artist.get_linewidths()
        if len(widths):
            for index, path in enumerate(artist.get_paths()):
                yield path, widths[index % len(widths)]


def _edge_runs(artist, bounds, ax):
    to_data = artist.get_transform() - ax.transData
    limits = bounds.get_points().T
    for path, width in _strokes(artist):
        vertices = to_data.transform(path.vertices)
        if len(vertices) < 2 or width <= 0:
            continue
        for normal in (0, 1):
            along = 1 - normal
            low, high = limits[along]
            sides = limits[normal]
            for edge in sides:
                on_edge = np.isclose(vertices[:, normal], edge, rtol=0,
                                     atol=abs(sides[1] - sides[0]) * 1e-12)
                on_edge &= np.isfinite(vertices[:, along])
                segments = on_edge[:-1] & on_edge[1:]
                if path.codes is not None:
                    segments &= path.codes[1:] == Path.LINETO
                # Merge adjacent segments, including the samples of a Linear process.
                breaks = np.flatnonzero(np.diff(segments, prepend=False, append=False))
                for start, stop in breaks.reshape(-1, 2):
                    coords = vertices[start:stop + 1, along]
                    lo, hi = max(low, coords.min()), min(high, coords.max())
                    if lo < hi:
                        points = np.empty((2, 2))
                        points[:, along] = lo, hi
                        points[:, normal] = edge
                        yield Bbox(points), along, width


class _EdgeClip(Patch):
    def __init__(self, bounds, runs):
        super().__init__(transform=IdentityTransform(), clip_on=False,
                         facecolor='none', edgecolor='none')
        self.bounds = bounds
        self.runs = runs

    def get_path(self):
        # Compute half-strokes in display units so export DPI and resizing both work.
        def display_box(data_box):
            points = self.axes.transData.transform(data_box.get_points())
            return Bbox([points.min(axis=0), points.max(axis=0)])

        frame = display_box(self.bounds)
        boxes = [frame]
        for run, along, width in self.runs:
            box = display_box(run).padded(width / 2 * self.figure.dpi / 72)
            # Stop a line flush where it crosses a perpendicular edge.
            ends = box.get_points()[:, along]
            ends[:] = ends.clip(*frame.get_points()[:, along])
            boxes.append(box)
        square = Path.unit_rectangle()
        return Path.make_compound_path(*(square.transformed(BboxTransformTo(b)) for b in boxes))

    def draw(self, renderer):
        # This patch participates in clipping and layout only.
        self.stale = False


def clip_curves(ax, xlim, ylim):
    for patch in ax.patches:
        if isinstance(patch, _EdgeClip):
            patch.remove()
    bounds = Bbox.from_extents(min(xlim), min(ylim), max(xlim), max(ylim))
    rectangle = Rectangle(bounds.p0, bounds.width, bounds.height, transform=ax.transData)
    for artist in [*ax.lines, *ax.collections]:
        if not artist.get_clip_on():
            continue
        runs = list(_edge_runs(artist, bounds, ax))
        if runs:
            # The unpainted patch also includes the outer half-stroke in a tight save.
            mask = ax.add_artist(_EdgeClip(bounds, runs))
            artist.set_clip_box(None)
            artist.set_clip_path(mask)
        else:
            artist.set_clip_path(rectangle)
