import flask
from flask import session
from services import data_loader
from services import data_saver
from services import preprocessor
from services import etc
import os

blueprint = flask.Blueprint(
    "preprocess",
    __name__,
    template_folder='templates'
)


# ========= Заглавная страница ===============
@blueprint.route("/preprocess/")
def preproc_page():
    if not etc.check_loaded_file():
        return flask.redirect('/loadpage/')
    frames = [data_loader.load_workfile()]
    plot = etc.make_single_plot(frames)
    return flask.render_template(
        'preprocess/preproc_page.html',
        plot_script=plot.get('script'),
        plot_div=plot.get('div'),
        js_resources=plot.get('js_res'),
        css_resources=plot.get('css_res')
    )


# ===========================================


# ========= Дедупликатор =====================
@blueprint.route("/preprocess/deduplication/")
def prep_dedup_page():
    frames = [data_loader.load_workfile()]
    plot = etc.make_single_plot(frames)
    return flask.render_template(
        'preprocess/pre_dedup.html',
        plot_script=plot.get('script'),
        plot_div=plot.get('div'),
        js_resources=plot.get('js_res'),
        css_resources=plot.get('css_res')
    )


@blueprint.route("/preprocess/deduplication/apply/", methods=['POST'])
def apply_deduplicate():
    buffer = data_loader.load_workfile()
    new_data = preprocessor.deduplicate(buffer)
    data_saver.save_data(new_data)
    return flask.redirect("/preprocess/deduplication/")
# ============================================


# ========= Преобразователь период-к-периоду ========
@blueprint.route("/preprocess/poping/")
def prep_poping_page():
    frames = [data_loader.load_workfile()]
    plot = etc.make_single_plot(frames)
    return flask.render_template(
        'preprocess/pre_poping.html',
        plot_script=plot.get('script'),
        plot_div=plot.get('div'),
        js_resources=plot.get('js_res'),
        css_resources=plot.get('css_res'),
        columns=session['columns']
    )


@blueprint.route("/preprocess/poping/apply/", methods=['POST'])
def apply_poping():
    buffer = data_loader.load_workfile()
    new_data = preprocessor.reshape_to_period_over_period(
        buffer,
        flask.request.form.get('column_name')
    )
    data_saver.save_data(new_data)
    return flask.redirect("/preprocess/poping/")
# ===================================================


# ========= Нормализатор ============================
@blueprint.route("/preprocess/normalize/")
def pre_norm_page():
    frames = [data_loader.load_workfile()]
    plot = etc.make_single_plot(frames)
    columns = ['Все']
    for col in session['columns']:
        columns.append(col)
    return flask.render_template(
        'preprocess/pre_norm.html',
        plot_script=plot.get('script'),
        plot_div=plot.get('div'),
        js_resources=plot.get('js_res'),
        css_resources=plot.get('css_res'),
        columns=columns
    )


@blueprint.route("/preprocess/normalize/apply/", methods=['POST'])
def apply_normalize():
    buffer = data_loader.load_workfile()
    new_data = preprocessor.auto_normalize(
        buffer,
        flask.request.form.get('column_name')
    )
    data_saver.save_data(new_data)
    return flask.redirect("/preprocess/normalize/")


# ===================================================


# ============ Вычитание со сдвигом =================
@blueprint.route("/preprocess/differ/")
def pre_diff_page():
    frames = [data_loader.load_workfile()]
    plot = etc.make_single_plot(frames)
    return flask.render_template(
        'preprocess/pre_differ.html',
        plot_script=plot.get('script'),
        plot_div=plot.get('div'),
        js_resources=plot.get('js_res'),
        css_resources=plot.get('css_res'),
        columns=session['columns']
    )


@blueprint.route("/preprocess/differ/apply/", methods=['POST'])
def diff_apply():
    import statsmodels.api as sm
    import matplotlib.pyplot as plt

    lag = flask.request.form.get('lag')
    col_name = flask.request.form.get('column_name')
    buffer = data_loader.load_workfile()
    buffer = buffer[col_name]
    lag_count = abs(len(buffer)/2) - 1
    buffer_diff = preprocessor.differ_x(buffer, lag)
    if preprocessor.is_stationary(buffer):
        stationary = 'Ряд стационарный'
    else:
        stationary = 'Ряд нестационарный'

    plot = etc.make_single_plot(
        [buffer, buffer_diff],
        name='Разность рядов. Сдвиг ' + lag
    )

# ============= Подготовка и дамп на диск графического ==============
#                     представления автокорреляции
    # TODO: Вынести во внешний модуль
    fig2 = plt.figure(figsize=(12, 8))
    ax1 = fig2.add_subplot(211)
    fig2 = sm.graphics.tsa.plot_acf(
        buffer.values.squeeze(),
        lags=lag_count,
        ax=ax1
    )
    ax2 = fig2.add_subplot(212)
    fig2 = sm.graphics.tsa.plot_pacf(buffer, lags=lag_count, ax=ax2)
    plt.savefig(
        os.path.join(
            os.getcwd(),
            'static',
            'img',
            str(session['uid']) + '_acf'
        )
    )
# ===================================================================
    acf_img = os.path.join('/static', 'img', str(session['uid']) + '_acf.png')

    return flask.render_template(
        'preprocess/pre_differ.html',
        plot_script=plot.get('script'),
        plot_div=plot.get('div'),
        js_resources=plot.get('js_res'),
        css_resources=plot.get('css_res'),
        columns=[col_name],
        acf_img=acf_img,
        stationary=stationary
    )
# ===================================================


# ================ Удаление строк в начале =====================
@blueprint.route("/preprocess/dropstrings/")
def pre_drops_page():
    frame = data_loader.load_workfile()
    frame = frame.drop(frame.index[[0]])
    data_saver.save_data(frame)
    return flask.redirect("/preprocess/")
# ==============================================================
