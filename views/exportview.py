import flask
import pandas as pd
from services import data_saver
from services import data_loader
from services import etc
from services import processor

blueprint = flask.Blueprint("Export_page", __name__, template_folder='templates')

@blueprint.route('/export/')
def export_page():
    if not etc.check_loaded_file():
        return flask.redirect('/loadpage/')
    return flask.render_template('export_page.html')


@blueprint.route('/export/dataset/')
def export_current_data():
    data_frame = data_loader.load_workfile('_forecasted')
    filepath = data_saver.show_save_dialog(
        'Сохранить файл данных',
        (('Excel 2010', '*.xlsx'), ('Все файлы', '*.*'))
    )
    data_saver.save_to_excel(data_frame.round(3), filepath)

    try:
        basis_frame = data_loader.load_workfile('_basis_forecasted')
        data_saver.append_to_excel(filepath, basis_frame.round(3), sheet_name='Базисные значения')
    except FileNotFoundError:
        print('!!!======  Нет файла прогноза базисов. ======!!!')

    try:
        nn_frame = data_loader.load_workfile('_forecasted_weird')
        data_saver.append_to_excel(filepath, nn_frame, sheet_name='Прогноз по моделям машинного обучения')
    except FileNotFoundError:
        print('!!!======  Нет файла прогноза машинным обучением. ======!!!')

    try:
        data_frame = data_loader.load_workfile()
        describe_stat = pd.DataFrame(processor.describe(data_frame))
        data_saver.append_to_excel(filepath, describe_stat.round(3), sheet_name='Описательные статистики')
    except Exception:
        print('Ошибка с описательной статистикой')
    return flask.redirect('/export/')
