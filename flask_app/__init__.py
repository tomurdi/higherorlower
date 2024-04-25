# 3rd-party packages
from flask import Flask, render_template, request, redirect, url_for
from flask_mongoengine import MongoEngine
from flask_login import (
    LoginManager,
    current_user,
    login_user,
    logout_user,
    login_required,
)
from flask_bcrypt import Bcrypt
from werkzeug.utils import secure_filename
import os
from .client import GameClient

db = MongoEngine()
login_manager = LoginManager()
bcrypt = Bcrypt()
game_client = GameClient()


from .users.routes import users
from .main.routes import main
from .game.routes import game


def custom_404(e):
    return render_template("404.html"), 404

def create_app(test_config=None):
    # Create the Flask app
    app = Flask(__name__)

    # Load the default configuration
    app.config.from_pyfile("config.py", silent=False)

    # If a test configuration is passed, load it
    if test_config is not None:
        app.config.update(test_config)

    # Initialize extensions with the app
    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)

    # Register blueprints with the app
    

    app.register_blueprint(users)
    app.register_blueprint(main)
    app.register_blueprint(game)


    # Register custom error handlers
    app.register_error_handler(404, custom_404)

    # Specify the login view
    login_manager.login_view = "users.login_route"

    return app