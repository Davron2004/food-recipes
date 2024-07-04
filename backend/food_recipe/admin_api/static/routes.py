from flask import (
    Blueprint,
    send_from_directory,
)
from food_recipe import app


static = Blueprint('admin_static', __name__)

@static.route('/manage/')
def index():
    return send_from_directory(app.config['STATIC_FOLDER'], 'index.html')

@static.route('/manage/<path:path>')
def internal(path):
    return send_from_directory(app.config['STATIC_FOLDER'], 'index.html')

@static.route('/manage/favicon.ico')
def favicon():
    return send_from_directory(app.config['STATIC_FOLDER'], 'favicon.ico')

@static.route('/manage/assets/<path:filename>')
def serve_static(filename):
    return send_from_directory(app.config['STATIC_FOLDER'] + '/assets', filename)
