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

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)


class Venue(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(200), nullable=False)