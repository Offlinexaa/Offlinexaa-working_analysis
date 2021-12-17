import flask
from flask import session

app = flask.Flask(__name__)

# Генерируем ключ для поддержки сессий и cookie
app.secret_key = 'd2yi346f^^&giwhdwsfjdlwefwekfh23r423rwe'

def main():
    register_blueprints()               # регистрируем подготовленные шаблоны
    app.run(debug=False)                 # Запускаем сервер


def register_blueprints():
    # from views import helloview
    from views import loadview          # Часть, отвечающая за загрузку данных
    from views import mainview          # Окно приветствия
    from views import preprocview       # Часть, отвечающая за предварительную обработку
    from views import procview          # Часть, отвечающая за основную обработку
    from views import layoutview        # Часть, отвечающая за разложение на раздельные графики
    from views import exportview        # Окно экспорта

    # app.register_blueprint(helloview.blueprint)
    app.register_blueprint(mainview.blueprint)
    app.register_blueprint(loadview.blueprint)
    app.register_blueprint(preprocview.blueprint)
    app.register_blueprint(procview.blueprint)
    app.register_blueprint(layoutview.blueprint)
    app.register_blueprint(exportview.blueprint)


if __name__ == '__main__':
    main()
