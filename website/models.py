from . import db
from datetime import datetime
from flask_login import UserMixin

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(100), nullable=False)
    surname = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120),unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    contact_number = db.Column(db.String(20), nullable=False)
    street_address = db.Column(db.String(200), nullable=False)

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    