import flask
import uuid

from services.etc import check_and_create_dirs


blueprint = flask.Blueprint("home", __name__, template_folder='templates')
filename = 'Empty'


@blueprint.route("/")
def main_page():
    flask.session['uid'] = uuid.uuid4()
    check_and_create_dirs()
    return flask.render_template('main_page.html')
