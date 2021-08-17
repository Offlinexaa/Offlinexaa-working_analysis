import flask
import uuid


blueprint = flask.Blueprint("home", __name__, template_folder='templates')
filename = 'Empty'


@blueprint.route("/")
def main_page():
    flask.session['uid'] = uuid.uuid4()
    return flask.render_template('main_page.html')
