from . import db
from flask_login import UserMixin

class Video(db.Model):
    name = db.Column(db.String(100))
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    processing = db.Column(db.Boolean, unique=False, default=False)
    failed = db.Column(db.Boolean, unique=False, default=False)
    done = db.Column(db.Boolean, unique=False, default=False)
    in_queue = db.Column(db.Boolean, unique=False, default=True)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    alerts = db.Column(db.String(150))
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    name = db.Column(db.String(150))
    videos = db.relationship('Video')