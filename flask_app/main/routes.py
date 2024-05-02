from flask import Blueprint, render_template, current_app
from flask_bcrypt import Bcrypt
from flask_pymongo import PyMongo

main = Blueprint('main', __name__)
bcrypt = Bcrypt()

@main.route('/')
@main.route('/index')
def index():
    return render_template('index.html')