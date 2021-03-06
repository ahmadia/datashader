from __future__ import absolute_import, division

from toolz import memoize

from .utils import ngjit, isreal


class Glyph(object):
    pass


class Point(Glyph):
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def validate(self, in_dshape):
        if not isreal(in_dshape.measure[self.x]):
            raise ValueError('x must be real')
        elif not isreal(in_dshape.measure[self.y]):
            raise ValueError('y must be real')

    @memoize
    def _build_extend(self, x_mapper, y_mapper, info, append):
        x_name = self.x
        y_name = self.y

        @ngjit
        def _extend(vt, bounds, xs, ys, *aggs_and_cols):
            sx, tx, sy, ty = vt
            xmin, xmax, ymin, ymax = bounds
            for i in range(xs.shape[0]):
                x = xs[i]
                y = ys[i]
                if (xmin <= x <= xmax) and (ymin <= y <= ymax):
                    append(i,
                           int(x_mapper(x) * sx + tx),
                           int(y_mapper(y) * sy + ty),
                           *aggs_and_cols)

        def extend(aggs, df, vt, bounds):
            xs = df[x_name].values
            ys = df[y_name].values
            cols = aggs + info(df)
            _extend(vt, bounds, xs, ys, *cols)

        return extend

    def _compute_x_bounds(self, df):
        return df[self.x].min(), df[self.y].max()

    def _compute_y_bounds(self, df):
        return df[self.y].min(), df[self.y].max()
