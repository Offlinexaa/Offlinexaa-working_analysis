import flask
import os
from flask import session
from services import data_saver
from services import data_loader
from services import etc

blueprint = flask.Blueprint("Export_page", __name__, template_folder='templates')

@blueprint.route('/export/')
def export_page():
    if not etc.check_loaded_file():
        return flask.redirect('/loadpage/')
    return flask.render_template('export_page.html')


@blueprint.route('/export/dataset/')
def export_current_data():
    filepath = os.path.join(os.getcwd(), 'static', 'current_data', str(session['uid']) + '_'
                            + 'forecasted.xlsx')
    data_frame = data_loader.load_data(file_name=filepath, file_type='xlsx')
    filepath = data_saver.show_save_dialog(
        'Сохранить файл данных',
        (('Excel 2010', '*.xlsx'), ('Все файлы', '*.*'))
    )
    data_saver.save_to_excel(data_frame, filepath)
    return flask.redirect('/export/')
