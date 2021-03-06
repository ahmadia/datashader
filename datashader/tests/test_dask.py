import numpy as np
import pandas as pd
import xarray as xr
import dask.dataframe as dd
from dask.context import set_options
from dask.async import get_sync

import datashader as ds

set_options(get=get_sync)

df = pd.DataFrame({'x': np.array(([0.] * 10 + [1] * 10)),
                   'y': np.array(([0.] * 5 + [1] * 5 + [0] * 5 + [1] * 5)),
                   'log_x': np.array(([1.] * 10 + [10] * 10)),
                   'log_y': np.array(([1.] * 5 + [10] * 5 + [1] * 5 + [10] * 5)),
                   'i32': np.arange(20, dtype='i4'),
                   'i64': np.arange(20, dtype='i8'),
                   'f32': np.arange(20, dtype='f4'),
                   'f64': np.arange(20, dtype='f8'),
                   'cat': ['a']*5 + ['b']*5 + ['c']*5 + ['d']*5})
df.cat = df.cat.astype('category')
df.f32[2] = np.nan
df.f64[2] = np.nan

ddf = dd.from_pandas(df, npartitions=3)

c = ds.Canvas(plot_width=2, plot_height=2, x_range=(0, 1), y_range=(0, 1))
c_logx = ds.Canvas(plot_width=2, plot_height=2, x_range=(1, 10),
                   y_range=(0, 1), x_axis_type='log')
c_logy = ds.Canvas(plot_width=2, plot_height=2, x_range=(0, 1),
                   y_range=(1, 10), y_axis_type='log')
c_logxy = ds.Canvas(plot_width=2, plot_height=2, x_range=(1, 10),
                    y_range=(1, 10), x_axis_type='log', y_axis_type='log')

coords = [np.arange(2, dtype='f8'), np.arange(2, dtype='f8')]
dims = ['y_axis', 'x_axis']


def assert_eq(agg, b):
    assert agg.equals(b)


def test_count():
    out = xr.DataArray(np.array([[5, 5], [5, 5]], dtype='i4'),
                       coords=coords, dims=dims)
    assert_eq(c.points(ddf, 'x', 'y', ds.count('i32')), out)
    assert_eq(c.points(ddf, 'x', 'y', ds.count('i64')), out)
    assert_eq(c.points(ddf, 'x', 'y', ds.count()), out)
    out = xr.DataArray(np.array([[4, 5], [5, 5]], dtype='i4'),
                       coords=coords, dims=dims)
    assert_eq(c.points(ddf, 'x', 'y', ds.count('f32')), out)
    assert_eq(c.points(ddf, 'x', 'y', ds.count('f64')), out)


def test_sum():
    out = xr.DataArray(df.i32.reshape((2, 2, 5)).sum(axis=2, dtype='f8').T,
                       coords=coords, dims=dims)
    assert_eq(c.points(ddf, 'x', 'y', ds.sum('i32')), out)
    assert_eq(c.points(ddf, 'x', 'y', ds.sum('i64')), out)
    out = xr.DataArray(np.nansum(df.f64.reshape((2, 2, 5)), axis=2).T,
                       coords=coords, dims=dims)
    assert_eq(c.points(ddf, 'x', 'y', ds.sum('f32')), out)
    assert_eq(c.points(ddf, 'x', 'y', ds.sum('f64')), out)


def test_min():
    out = xr.DataArray(df.i64.reshape((2, 2, 5)).min(axis=2).astype('f8').T,
                       coords=coords, dims=dims)
    assert_eq(c.points(ddf, 'x', 'y', ds.min('i32')), out)
    assert_eq(c.points(ddf, 'x', 'y', ds.min('i64')), out)
    assert_eq(c.points(ddf, 'x', 'y', ds.min('f32')), out)
    assert_eq(c.points(ddf, 'x', 'y', ds.min('f64')), out)


def test_max():
    out = xr.DataArray(df.i64.reshape((2, 2, 5)).max(axis=2).astype('f8').T,
                       coords=coords, dims=dims)
    assert_eq(c.points(ddf, 'x', 'y', ds.max('i32')), out)
    assert_eq(c.points(ddf, 'x', 'y', ds.max('i64')), out)
    assert_eq(c.points(ddf, 'x', 'y', ds.max('f32')), out)
    assert_eq(c.points(ddf, 'x', 'y', ds.max('f64')), out)


def test_mean():
    out = xr.DataArray(df.i32.reshape((2, 2, 5)).mean(axis=2, dtype='f8').T,
                       coords=coords, dims=dims)
    assert_eq(c.points(ddf, 'x', 'y', ds.mean('i32')), out)
    assert_eq(c.points(ddf, 'x', 'y', ds.mean('i64')), out)
    out = xr.DataArray(np.nanmean(df.f64.reshape((2, 2, 5)), axis=2).T,
                       coords=coords, dims=dims)
    assert_eq(c.points(ddf, 'x', 'y', ds.mean('f32')), out)
    assert_eq(c.points(ddf, 'x', 'y', ds.mean('f64')), out)


def test_var():
    out = xr.DataArray(df.i32.reshape((2, 2, 5)).var(axis=2, dtype='f8').T,
                       coords=coords, dims=dims)
    assert_eq(c.points(ddf, 'x', 'y', ds.var('i32')), out)
    assert_eq(c.points(ddf, 'x', 'y', ds.var('i64')), out)
    out = xr.DataArray(np.nanvar(df.f64.reshape((2, 2, 5)), axis=2).T,
                       coords=coords, dims=dims)
    assert_eq(c.points(ddf, 'x', 'y', ds.var('f32')), out)
    assert_eq(c.points(ddf, 'x', 'y', ds.var('f64')), out)


def test_std():
    out = xr.DataArray(df.i32.reshape((2, 2, 5)).std(axis=2, dtype='f8').T,
                       coords=coords, dims=dims)
    assert_eq(c.points(ddf, 'x', 'y', ds.std('i32')), out)
    assert_eq(c.points(ddf, 'x', 'y', ds.std('i64')), out)
    out = xr.DataArray(np.nanstd(df.f64.reshape((2, 2, 5)), axis=2).T,
                       coords=coords, dims=dims)
    assert_eq(c.points(ddf, 'x', 'y', ds.std('f32')), out)
    assert_eq(c.points(ddf, 'x', 'y', ds.std('f64')), out)


def test_count_cat():
    sol = np.array([[[5, 0, 0, 0],
                     [0, 0, 5, 0]],
                    [[0, 5, 0, 0],
                     [0, 0, 0, 5]]])
    out = xr.DataArray(sol, coords=(coords + [['a', 'b', 'c', 'd']]),
                       dims=(dims + ['cat']))
    agg = c.points(ddf, 'x', 'y', ds.count_cat('cat'))
    assert_eq(agg, out)


def test_multiple_aggregates():
    agg = c.points(ddf, 'x', 'y',
                   ds.summary(f64_std=ds.std('f64'),
                              f64_mean=ds.mean('f64'),
                              i32_sum=ds.sum('i32'),
                              i32_count=ds.count('i32')))

    f = lambda x: xr.DataArray(x, coords=coords, dims=dims)
    assert_eq(agg.f64_std, f(np.nanstd(df.f64.reshape((2, 2, 5)), axis=2).T))
    assert_eq(agg.f64_mean, f(np.nanmean(df.f64.reshape((2, 2, 5)), axis=2).T))
    assert_eq(agg.i32_sum, f(df.i32.reshape((2, 2, 5)).sum(axis=2, dtype='f8').T))
    assert_eq(agg.i32_count, f(np.array([[5, 5], [5, 5]], dtype='i4')))


def test_log_axis():
    sol = np.array([[5, 5], [5, 5]], dtype='i4')
    out = xr.DataArray(sol, coords=[np.array([0., 1.]), np.array([1., 10.])],
                       dims=dims)
    assert_eq(c_logx.points(ddf, 'log_x', 'y', ds.count('i32')), out)
    out = xr.DataArray(sol, coords=[np.array([1., 10.]), np.array([0., 1.])],
                       dims=dims)
    assert_eq(c_logy.points(ddf, 'x', 'log_y', ds.count('i32')), out)
    out = xr.DataArray(sol, coords=[np.array([1., 10.]), np.array([1., 10.])],
                       dims=dims)
    assert_eq(c_logxy.points(ddf, 'log_x', 'log_y', ds.count('i32')), out)
