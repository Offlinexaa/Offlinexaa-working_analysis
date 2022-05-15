import flask
import uuid

blueprint = flask.Blueprint("hello", __name__, template_folder='templates')


@blueprint.route("/")
def main_page():
    flask.session['uid'] = uuid.uuid4()
    print('uid=' + flask.session['uid'])
    return flask.render_template('main_page.html')
