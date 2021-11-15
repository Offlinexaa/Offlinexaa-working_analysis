import flask
import pandas
from flask import session
from services import data_loader
from services import data_saver
from services import etc
from bokeh.layouts import gridplot
from bokeh.plotting import figure
from bokeh.palettes import Category20_10 as palette
from bokeh.resources import INLINE
from bokeh.embed import components
import math
import itertools


blueprint = flask.Blueprint('layout', __name__, template_folder='templates')


@blueprint.route('/visualize/')
def layout_page():
    if not etc.check_loaded_file():
        return flask.redirect('/loadpage/')
    etc.init_model()
    return flask.redirect('/visualize/grid/')


@blueprint.route('/visualize/grid/')
def layout_grid_page():
    buffer = data_loader.load_workfile()
    plot = etc.make_grid_plot(buffer)
    return flask.render_template('layout/grid_layout_page.html',
                                 plot_script=plot.get('script'), plot_div=plot.get('div'),
                                 js_resources=plot.get('js_res'), css_resources=plot.get('css_res'))


@blueprint.route('/visualize/grid/basis/')
def layout_grid_basis_page():
    from services import preprocessor
    if 'basis_mode' in flask.session:
        mode = flask.session['basis_mode']
    else:
        mode = 'abs'
        flask.session['basis_mode'] = mode
    buffer = data_loader.load_workfile()
    buffer = preprocessor.df_to_base(buffer, mode)
    data_saver.save_data(buffer, '_basis')
    plot = etc.make_grid_plot(buffer)
    return flask.render_template('layout/grid_base_layout_page.html',
                                 plot_script=plot.get('script'), plot_div=plot.get('div'),
                                 js_resources=plot.get('js_res'), css_resources=plot.get('css_res'))


@blueprint.route('/visualize/grid/set_mode_abs')
def set_basis_mode_abs():
    flask.session['basis_mode'] = 'abs'
    return flask.redirect('/visualize/grid/basis/')


@blueprint.route('/visualize/grid/set_mode_add')
def set_basis_mode_add():
    flask.session['basis_mode'] = 'add'
    return flask.redirect('/visualize/grid/basis/')


@blueprint.route('/visualize/grid/forecast/setup/')
def layout_grid_forecast_setup_page():
    return flask.render_template("layout/grid_forecast_setup_page.html", models=session['models'])


@blueprint.route('/visualize/grid/forecast/setup/<column_name>')
def layout_grid_forecast_setup_per_column(column_name: str):
    filepath = data_loader.show_open_dialog(title="Выберите модель для столбца " + column_name,
                                            filetypes=(('Модель анализа', '*.mdl'),
                                                       ('Все файлы', '*.*')))
    etc.update_model_dict(column_name, filepath)
    return flask.redirect('/visualize/grid/forecast/setup/')


# TODO: вынести во внешний модуль функционал
@blueprint.route('/visualize/grid/forecast/')
def layout_grid_forecast_page():
    # import statsmodels.api as sm
    import datetime
    # from pprint import pprint
    buffer = data_loader.load_workfile()
    x_axis = buffer.index
    extended_axis = x_axis.to_list()
    # pprint(extended_axis)
    for r in range(12):
        extended_axis.append(extended_axis[-1] + datetime.timedelta(days=31))
    extended_axis = extended_axis[-13:]
    # pprint(extended_axis)
    colors = itertools.cycle(palette)
    figs = []
    # new_buffer = pandas.DataFrame()
    for col in buffer.columns:
        if session['models'].get(col) is not None:
            predict_model = data_loader.load_model(session['models'].get(col))
            prediction = predict_model.predict(start=len(x_axis), end=(len(x_axis) + 12), typ='levels')
            # new_buffer = new_buffer.assign(str=prediction)
            fig = figure(background_fill_color="#fafafa", x_axis_type='datetime')
            fig.line(x_axis, buffer[col], color=next(colors), legend_label=col)
            fig.line(extended_axis, prediction, color='green', line_width=3, legend_label=('Прогноз для ' + col))
            fig.legend.location = 'top_left'
            # fig.grid.click_policy="hide"
            figs.append(fig)
    n_cols = int(round(math.sqrt(len(figs))))
    # Debug info
    # ----------
    # print(n_cols)
    # ----------

    # Компоновка через layouts из bokeh
    grid = gridplot(figs, ncols=n_cols, sizing_mode="stretch_both", plot_width=250, plot_height=250)
    js_resources = INLINE.render_js()
    css_resources = INLINE.render_css()
    script, div = components(grid)
    return flask.render_template("layout/grid_forecast_page.html", plot_script=script, plot_div=div,
                                 js_resources=js_resources, css_resources=css_resources)


@blueprint.route('/visualize/grid/forecast/basis')
def layout_grid_forecast_basis_page():
    # import statsmodels.api as sm
    import datetime
    # from pprint import pprint
    buffer = data_loader.load_data(session['workfile']+'_basis.json', file_type='json', index_col='index')
    x_axis = buffer.index
    extended_axis = x_axis.to_list()
    # pprint(extended_axis)
    for r in range(5):
        extended_axis.append(extended_axis[-1] + datetime.timedelta(days=1))
    extended_axis = extended_axis[-6:]
    # pprint(extended_axis)
    colors = itertools.cycle(palette)
    figs = []
    for col in buffer.columns:
        if session['models'].get(col) is not None:
            predict_model = data_loader.load_model(session['models'].get(col))
            prediction = predict_model.predict(start=len(x_axis), end=(len(x_axis) + 5), typ='levels')
            fig = figure(background_fill_color="#fafafa", x_axis_type='datetime')
            fig.line(x_axis, buffer[col], color=next(colors), legend_label=col)
            fig.line(extended_axis, prediction, color='green', line_width=3, legend_label=('Прогноз для ' + col))
            fig.legend.location = 'top_left'
            # fig.grid.click_policy="hide"
            figs.append(fig)
    n_cols = int(round(math.sqrt(len(figs))))
    # Debug info
    # ----------
    # print(n_cols)
    # ----------

    # Компоновка через layouts из bokeh
    grid = gridplot(figs, ncols=n_cols, sizing_mode="stretch_both", plot_width=250, plot_height=250)
    js_resources = INLINE.render_js()
    css_resources = INLINE.render_css()
    script, div = components(grid)
    return flask.render_template("layout/grid_forecast_page.html", plot_script=script, plot_div=div,
                                 js_resources=js_resources, css_resources=css_resources)


# ================ Компановка вручную ===================
# Можно настроить более гибко, но сложно, долго и
# значительно медленнее работает. Пока отключено.
# @blueprint.route('/visualize/manual/')
# def layout_manual_page():
#     buffer = data_loader.load_workfile()
#     x_axis = buffer.index
#     colors = itertools.cycle(palette)
#     components_list = []
#     for col in session['columns']:
#         color = next(colors)
#         fig = figure(background_fill_color="#fafafa", x_axis_type='datetime')
#         fig.line(x_axis, buffer[col], line_width=2, color=color)
#         # btn = Button(def lambda: return print(col))
#         colum = column(fig)
#         script, div = components(colum)
#     js_resources = INLINE.render_js()
#     css_resources = INLINE.render_css()
#     script, div = components()
#     return flask.render_template('layout/manual_layout_page.html', plot_script=script, plot_div=div, js_resources=js_resources,
#                                  css_resources=css_resources)
# =======================================================