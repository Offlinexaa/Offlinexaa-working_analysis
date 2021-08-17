import flask
from flask import request
from services import data_loader
from services import data_saver
from services import etc


blueprint = flask.Blueprint("load", __name__, template_folder='templates')
file_types = ['xlsx', 'json', 'csv']


@blueprint.route("/loadpage/")
def load_page():
    # Это нужно для красоты: при нажатии на кнопки приходится менять путь
    # и перерисовывать шаблон. Если файл уже был указан, то пишем его
    # путь в поле для ввода
    if 'filename' in flask.session:
        file_path = flask.session['filename']
    else:
        file_path = "Файл не выбран"
    return flask.render_template('load_page.html', file_types=file_types, file_path=file_path)


@blueprint.route("/loadpage/openfile/", methods=['POST'])
def lod_file():
    mode = request.form.get('mode')
    if mode == 'url':
        url = request.form.get('path')
        dest_file = 'getfile.xlsx'
        frame = data_loader.url_load(url=url, filepath=dest_file)
        flask.session['filename'] = dest_file
        data_saver.init_save_path()
        data_saver.save_data(data=frame)
        data_saver.save_to_excel(data=frame, filepath=dest_file)
        flask.session['columns'] = frame.columns.to_list()
        return flask.render_template('load_page.html', file_path=flask.session['filename'], form_text="Файл загружен",
                                     form_text_mode="text-success", file_types=file_types)
    if 'filename' in flask.session:
        file_type = request.form.get('format')
        etc.clear_session('models')
        frame = data_loader.load_data(flask.session['filename'], file_type, index_col='index')
        flask.session['columns'] = frame.columns.to_list()
        data_saver.init_save_path()
        data_saver.save_data(frame)
        return flask.render_template('load_page.html', file_path=flask.session['filename'], form_text="Файл загружен",
                                     form_text_mode="text-success", file_types=file_types)
    else:
        return flask.render_template('load_page.html', form_text="Не выбран файл", form_text_mode="text-danger",
                                     file_types=file_types)


@blueprint.route("/loadpage/selectfile/")
def select_file():
    flask.session['filename'] = data_loader.show_open_dialog(title='Выберите ряд данных',
                                                             filetypes=(('MS Office', '*.xlsx *.xls'),
                                                                        ('JSON', '*.json'),
                                                                        ('CSV', '*.csv'),
                                                                        ('Все файлы', '*.*')))
    return flask.redirect("/loadpage/")
