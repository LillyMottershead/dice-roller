
import os
import json
from flask import (
    Flask, render_template, render_template, request, session, url_for
)
from .roll_parser import (
    parse_command, aliases, RollEquation
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
                rolls = parse_command(command)
                rolls_as_dicts = []
                for roll in rolls:
                    roll_dict = {'str': str(roll),
                                 'is_roll': type(roll) is RollEquation,
                                }
                    if roll_dict['is_roll']:
                        roll_dict['images'] = [url_for('static', filename=f'dice/{filename}') for filename in roll.dice_image_filenames()]
                        roll_dict['total'] = roll.result()
                    rolls_as_dicts.append(roll_dict)
                session['last'] = rolls_as_dicts
                reverse_rolls_as_dicts = rolls_as_dicts.copy()
                reverse_rolls_as_dicts.reverse()
                session['log'] = [roll['str'] for roll in reverse_rolls_as_dicts] + session.get('log')
            if request.form.get('clear'):
                session['log'] = []
        session['aliases'] = list(aliases)
        return render_template('index.html')

    return app