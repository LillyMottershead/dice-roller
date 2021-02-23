import os

from flask import (
    Flask, render_template, request
)
from .parser.dice_parser import parse_command


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    @app.route('/', methods=('GET', 'POST'))
    def index():
        response = 'test'
        if request.method == 'POST':
            command = request.form['command']
            response = parse_command(command)[0]
        return render_template('index.html', response=response)

    return app
