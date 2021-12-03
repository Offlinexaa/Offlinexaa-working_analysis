import os

import pandas as pd
from flask import session
from bokeh.plotting import figure
from bokeh.resources import INLINE
from bokeh.embed import components
from bokeh.palettes import Category20_10 as palette
from pathlib import Path
import itertools


def clear_session(name: str = None) -> bool:
    if name is None:
        return False
    if name in session:
        session.pop(name)
        return True
    else:
        return False


def init_model():
    if not ('models' in session):
        models = {}
        for col in session['columns']:
            models.update({col: None})
        session['models'] = models


def check_loaded_file() -> bool:
    if 'filename' in session:
        return True
    return False


def make_single_plot(frames: list, name: str = 'Текущие данные') -> dict:
    fig = figure(title=name, plot_width=1000, x_axis_type='datetime')
    colors = itertools.cycle(palette)
    for df_v in frames:
        axis_x = df_v.index
        if isinstance(df_v, pd.DataFrame):
            for column in df_v.columns:
                fig.line(axis_x, df_v[column], line_width=2, color=next(colors))
        elif isinstance(df_v, pd.Series):
            fig.line(axis_x, df_v, line_width=2, color=next(colors))
    script, div = components(fig)
    return {'js_res': INLINE.render_js(), 'css_res': INLINE.render_css(), 'script': script, 'div': div}


def make_grid_plot(data: pd.DataFrame) -> dict:
    from bokeh.layouts import gridplot
    import math

    x_axis = data.index
    colors = itertools.cycle(palette)
    figs = []
    for col in data.columns:
        fig = figure(background_fill_color="#fafafa", x_axis_type='datetime')
        fig.line(x_axis, data[col], color=next(colors), legend_label=col)
        fig.legend.location = 'top_left'
        figs.append(fig)
    n_cols = int(round(math.sqrt(len(figs))))
    if n_cols > 4:
        n_cols = 4
    grid = gridplot(figs, ncols=n_cols, sizing_mode="stretch_both", plot_width=250, plot_height=250)
    js_resources = INLINE.render_js()
    css_resources = INLINE.render_css()
    script, div = components(grid)

    return {'js_res': INLINE.render_js(), 'css_res': INLINE.render_css(), 'script': script, 'div': div}


def update_model_dict(column_name: str, filepath: str):
    """Меняет путь к файлу модели для ряда column_name.
    Если ряд отсутствует, добавляет его в словарь."""
    models = session['models']
    models.update({column_name: filepath})
    session['models'] = models


def check_and_create_dirs():
    curr_dir = os.path.join(os.getcwd(), 'static', 'current_data')
    model_dir = os.path.join(os.getcwd(), 'static', 'models')
    Path(curr_dir).mkdir(parents=True, exist_ok=True)
    Path(model_dir).mkdir(parents=True, exist_ok=True)
