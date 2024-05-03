from flask_login import UserMixin
from datetime import datetime
from . import db, login_manager
from mongoengine.fields import ListField, IntField

@login_manager.user_loader
def load_user(user_id):
    return User.objects(username=user_id).first()

class User(db.Document, UserMixin):
    email = db.EmailField(unique=True, required=True)
    username = db.StringField(unique=True, required=True)
    password = db.StringField(required=True)
    profile_pic = db.ImageField()
    highScore = IntField()
    scores = ListField(IntField())

    def get_id(self):
        return self.username