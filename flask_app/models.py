from flask_login import UserMixin
from datetime import datetime
from . import db, login_manager


class User(db.Document, UserMixin):
    email = db.EmailField(unique=True, required=True)
    username = db.StringField(unique=True, required=True)
    password = db.StringField(required=True)
    profile_pic = db.ImageField()
    #TODO: I think we need a highscore option here

    def get_id(self):
        return self.username