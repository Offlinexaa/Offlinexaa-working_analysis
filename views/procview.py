import flask
from flask import session
from flask import Blueprint
from flask import redirect
from services import data_loader
from services import data_saver
from services import processor
from services import etc

blueprint = Blueprint("process", __name__, template_folder='templates')


# ========= Заглавная страница ===============
@blueprint.route("/process/")
def proc_page():
    if not etc.check_loaded_file():
        return flask.redirect('/loadpage/')
    frames = [data_loader.load_workfile()]
    plot = etc.make_single_plot(frames)
    return flask.render_template(
        'process/proc_page.html',
        plot_script=plot.get('script'),
        plot_div=plot.get('div'),
        js_resources=plot.get('js_res'),
        css_resources=plot.get('css_res')
    )
# ===========================================


# ========= Описательная статистика ===========
@blueprint.route("/process/describe/")
def proc_desc_page():

    frames = [data_loader.load_workfile()]
    plot = etc.make_single_plot(frames)

    describe_stat = processor.describe(frames[0])

    return flask.render_template(
        'process/proc_describe.html',
        describe_stat=describe_stat,
        plot_script=plot.get('script'),
        plot_div=plot.get('div'),
        js_resources=plot.get('js_res'),
        css_resources=plot.get('css_res')
    )
# =============================================


# ---------------------------------------------
# ============== Блок регрессий ===============
# ---------------------------------------------
# ============ Линейная регрессия =============
@blueprint.route("/process/regression_linear/")
def proc_regression_linear():
    frames = [data_loader.load_workfile()]
    plot = etc.make_single_plot(frames)
    return flask.render_template(
        'process/proc_regression_linear.html',
        columns=session['columns'],
        init_test_len=12,
        plot_script=plot.get('script'),
        plot_div=plot.get('div'),
        js_resources=plot.get('js_res'),
        css_resources=plot.get('css_res')
    )


@blueprint.route("/process/regression_linear/apply/", methods=['POST'])
def proc_regression_linear_apply():

    column = flask.request.form.get('column_name')
    predict_len = int(flask.request.form.get('test_data_length'))

    buffer = data_loader.load_workfile()
    buffer = buffer[column]

    result = processor.linear_regression(
        buffer,
        sample_len=24,
        predict_depth=predict_len
    )

    return flask.render_template(
        'process/proc_regression_linear.html',
        plot_script=result.get('script'),
        plot_div=result.get('div'),
        save_disabled='',
        js_resources=result.get('js_res'),
        css_resources=result.get('css_res'),
        columns=[column],
        init_test_len=predict_len
    )
# =============================================


# ============ Регрессия ARIMA ===============
@blueprint.route("/process/arima/")
def proc_regression_sarima():
    frames = [data_loader.load_workfile()]
    plot = etc.make_single_plot(frames)
    return flask.render_template(
        'process/proc_regression_arima.html',
        columns=session['columns'],
        init_p=0,
        init_d=0,
        init_q=0,
        init_test_len=0,
        plot_script=plot.get('script'),
        plot_div=plot.get('div'),
        js_resources=plot.get('js_res'),
        css_resources=plot.get('css_res')
    )


@blueprint.route("/process/arima/apply/", methods=['POST'])
def proc_regression_sarima_apply():
    column = flask.request.form.get('column_name')
    p = int(flask.request.form.get('sarima_p'))
    d = int(flask.request.form.get('sarima_d'))
    q = int(flask.request.form.get('sarima_q'))
    test_len = int(flask.request.form.get('test_data_length'))

    buffer = data_loader.load_workfile()
    buffer = buffer[column]

    result = processor.arima_regression(buffer, p, d, q, test_len)
    data_saver.save_model(result.get('model'))

    return flask.render_template(
        'process/proc_regression_arima.html',
        plot_script=result.get('script'),
        plot_div=result.get('div'),
        save_disabled='',
        js_resources=result.get('js_res'),
        css_resources=result.get('css_res'),
        columns=[column],
        init_p=p,
        init_d=d,
        init_q=q,
        init_test_len=test_len
    )


@blueprint.route("/process/arima/autotune/<column_name>")
def proc_regression_sarima_auto(column_name: str):
    buffer = data_loader.load_workfile()
    buffer = buffer[column_name]

    # print('Column name = ' + column_name)
    params = processor.adopt_arima(buffer)

    result = processor.arima_regression(
        buffer,
        params.get('p'),
        params.get('d'),
        params.get('q'),
        0
    )

    data_saver.save_model(result.get('model'))

    return flask.render_template(
        'process/proc_regression_arima.html',
        plot_script=result.get('script'),
        plot_div=result.get('div'),
        save_disabled='',
        js_resources=result.get('js_res'),
        css_resources=result.get('css_res'),
        columns=[column_name],
        init_p=params.get('p'),
        init_d=params.get('d'),
        init_q=params.get('q'),
        init_test_len=0
    )
# =============================================


# ============ Сохранение модели ==============
@blueprint.route("/process/arima/save/")
def proc_regression_sarima_save():
    filename = data_saver.show_save_dialog(
        title='Сохранить прогнозную модель',
        filetypes=(('Модель', '*.mdl'), ('Все файлы', '*.*'))
    )
    model = data_loader.load_model()
    data_saver.save_model(model, filename)
    return redirect("/process/arima/")
# =============================================


@blueprint.route("/process/auto_calculate_model/")
def proc_auto_calculate_model():
    import os

    buffer = data_loader.load_workfile()

    etc.init_model()

    for column_name in buffer.columns:
        work_column = buffer[column_name]
        params = processor.adopt_arima(work_column)
        result = processor.arima_regression(
            work_column,
            params.get('p'),
            params.get('d'),
            params.get('q'),
            0
        )
        filepath = os.path.join(
            os.getcwd(),
            'static',
            'models',
            str(session['uid']) + '_' + column_name + '.mdl'
        )
        data_saver.save_model(result.get('model'), filepath)
        etc.update_model_dict(column_name, filepath)

    return redirect("/process/")
# ---------------------------------------------
