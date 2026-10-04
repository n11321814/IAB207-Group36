from . import db
from datetime import datetime
from flask_login import UserMixin

# inherits from db.Model and UserMixin to create a user model for the database
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(100), nullable=False)
    surname = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    contact_number = db.Column(db.String(20), nullable=False)
    street_address = db.Column(db.String(200), nullable=False)

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(150), nullable=False)
    synopsis = db.Column(db.Text, nullable=False)
    poster_image = db.Column(db.String(300))
    classification = db.Column(db.String(10), nullable=False)
    runtime = db.Column(db.Integer, nullable=False)
    screening_format = db.Column(db.String(30))

    event_date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)

    ticket_price = db.Column(db.Numeric(6, 2), nullable=False)
    tickets_available = db.Column(db.Integer, nullable=False)
    tickets_remaining = db.Column(db.Integer, nullable=False)

    status = db.Column(db.String(20), nullable=False, default='Open')

    acknowledgement_type = db.Column(db.String(20), nullable=False, default='generic')
    acknowledgement_text = db.Column(db.Text)

    venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    organiser_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    created_on = db.Column(db.DateTime, default=datetime.utcnow)

    venue = db.relationship('Venue', backref='events')
    category = db.relationship('Category', backref='events')
    organiser = db.relationship('User', backref='events')

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