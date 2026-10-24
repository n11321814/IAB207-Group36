from . import db

from datetime import datetime, timedelta, timezone
from flask_login import UserMixin
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


def brisbane_now():
    #  fall back to a fixed UTC+10 offset if tzdata package is missing
    try:
        return datetime.now(ZoneInfo("Australia/Brisbane"))
    except ZoneInfoNotFoundError:
        return datetime.now(timezone(timedelta(hours=10)))

# inherits from db.Model to create a user model for the database
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(100), nullable=False)
    surname = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    contact_number = db.Column(db.String(20), nullable=False)
    street_address = db.Column(db.String(200), nullable=False)

# an event is a single film screening created by a organiser
class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(200), nullable=False)

    synopsis = db.Column(db.Text, nullable=False)

    poster_image = db.Column(db.String(350)) # optional URL to an image

    classification = db.Column(db.String(10), nullable=False) # see au classifications

    runtime = db.Column(db.Integer, nullable=False) # length in mins

    screening_format = db.Column(db.String(30))

    event_date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)

    ticket_price = db.Column(db.Numeric(6, 2), nullable=False)
    tickets_available = db.Column(db.Integer, nullable=False)
    tickets_remaining = db.Column(db.Integer, nullable=False)

    # Open, inactive, sold out, cancelled, only the application changes this not the user
    status = db.Column(db.String(20), nullable=False, default='Open')

    # acknowledgement of country none, generic or enhanced, text is only stored when the enhanced option is selected
    acknowledgement_type = db.Column(db.String(20), nullable=False, default='generic')
    acknowledgement_text = db.Column(db.Text)

    # foreign keys linking each event to its venue, category and organiser
    venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'), nullable=False)

    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    organiser_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    created_on = db.Column(db.DateTime, default=datetime.utcnow) # Not sure why this is crossed out

    # relationships let us write event.venue.name instead of doing a manual query
    venue = db.relationship('Venue', backref='events')
    category = db.relationship('Category', backref='events')
    organiser = db.relationship('User', backref='events')

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    content = db.Column(db.Text, nullable=False)
    posted_on = db.Column(db.DateTime, default=brisbane_now)
    
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    created_on = db.Column(db.DateTime, default=datetime.utcnow)

    event = db.relationship('Event', backref='comments')
    user = db.relationship('User', backref='comments')

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    quantity = db.Column(db.Integer, nullable=False)

    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    created_on = db.Column(db.DateTime, default=datetime.utcnow)
    created_on_local = db.Column(db.DateTime, default=brisbane_now)

    event = db.relationship('Event', backref='orders')
    user = db.relationship('User', backref='orders')

# look up table for categories shown on the event creation form
class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

# venue is are their own table so events can share same venue
class Venue(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(200), nullable=False)