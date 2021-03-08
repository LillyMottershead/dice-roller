import os

from flask import (
    Flask, render_template, render_template, request, session
)
from .roll_parser import parse_command


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.route('/', methods=('GET', 'POST'))
    def index():
        if 'log' not in session:
            session['log'] = []
        if request.method == 'POST':
            if command := request.form.get('command'):
                roll = parse_command(command)[0]
                roll_list = roll.split('\n')
                session['log'] = session.get('log') + roll_list
            if thing := request.form.get('clear'):
                session['log'] = []
        return render_template('index.html')

    return app
