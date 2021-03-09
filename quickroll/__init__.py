
import os
from flask import (
    Flask, render_template, render_template, request, session, url_for
)
from .roll_parser import (
    parse_command, aliases
)


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
        session['last'] = []
        if 'log' not in session:
            session['log'] = []
        if request.method == 'POST':
            if command := request.form.get('command'):
                roll = parse_command(command)
                session['last'] = roll[0].split('\n')
                session['dice_images'] = []
                if len(roll) > 1:
                    for thing in roll[1]:
                        session['dice_images'].append(url_for('static', filename=f'dice/{thing}'))
                session['log'] = session.get('log') + session.get('last')
            if request.form.get('clear'):
                session['log'] = []
        session['aliases'] = list(aliases)
        return render_template('index.html')

    return app