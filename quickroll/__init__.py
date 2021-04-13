
import os
import json
from flask import (
    Flask, flash, render_template, render_template, request, session, url_for
)
from werkzeug.utils import secure_filename
from .roll_parser import (
    parse_command, aliases, RollEquation, Roll
)


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
    )
    app.config['UPLOAD_FOLDER'] = '/uploads' 

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
        if 'last' not in session:
           session['last'] = []
        if 'log' not in session:
            session['log'] = []
        if request.method == 'POST':
            if command := request.form.get('command'):
                times = request.form.get('times') or 1
                session['last'] = []
                for _ in range(int(times)):
                    session['log'] = [f'> {command}'] + session['log']  
                    rolls = parse_command(command)
                    rolls_as_dicts = []
                    for roll in rolls:
                        roll_dict = {
                            'str': str(roll),
                            'is_roll': type(roll) is RollEquation,
                        }
                        if roll_dict['is_roll']:
                            roll_dict['images'] = [url_for('static', filename=filename) for filename in roll.dice_image_filenames()]
                            roll_dict['total'] = roll.result()
                            roll_dict['label'] = roll.label
                            roll_dict['is_crit'] = roll.is_crit()
                        rolls_as_dicts.append(roll_dict)
                        reverse_rolls_as_dicts = rolls_as_dicts.copy()
                        reverse_rolls_as_dicts.reverse()
                    session['log'] = [roll['str'] for roll in reverse_rolls_as_dicts] + session.get('log')
                    session['last'].append(rolls_as_dicts)
            if request.form.get('clear'):
                session['log'] = []
            if request.form.get('crit_rule'):
                Roll.crit_rule = request.form.get('crit_rule')
            if 'file' in request.files:
                file = request.files['import_file']
                if file.filename.endswith('.txt'):
                    for line in file:
                        line = line.decode('utf-8')
                        parse_command(str(line))


        session['aliases'] = list(aliases)
        return render_template('index.html')

    return app