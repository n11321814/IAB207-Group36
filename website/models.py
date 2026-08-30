from . import db
from datetime import datetime
from flask_login import UserMixin

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)