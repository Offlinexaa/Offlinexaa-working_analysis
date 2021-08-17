import flask
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
    init_frame = data_loader.load_workfile()
    base_frame = data_loader.load_basefile()
    filename = data_saver.show_save_dialog(filetypes=(('Microsoft Excel', '*.xlsx'), ))
    init_frame.to_excel(filename, sheet_name='Исходный ряд', engine='openpyxl')
    data_saver.append_to_excel(filename= filename, df= base_frame, sheet_name='Базисный ряд')
    return flask.redirect('/export/')
