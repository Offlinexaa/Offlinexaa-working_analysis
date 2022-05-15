import flask
# from flask import session

app = flask.Flask(__name__)


app.secret_key = 'd2yi346f^^&giwhdwsfjdlwefwekfh23r423rwe'


def main():
    register_blueprints()
    app.run(debug=False)   # Запускаем сервер


def register_blueprints():
    """Регистрируем шаблоны."""
    from views import (exportview, layoutview, loadview, mainview, preprocview,
                       procview)

    app.register_blueprint(mainview.blueprint)
    app.register_blueprint(loadview.blueprint)
    app.register_blueprint(preprocview.blueprint)
    app.register_blueprint(procview.blueprint)
    app.register_blueprint(layoutview.blueprint)
    app.register_blueprint(exportview.blueprint)


if __name__ == '__main__':
    main()
