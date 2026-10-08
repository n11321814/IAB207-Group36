from . import db
from datetime import datetime
from flask_login import UserMixin
from zoneinfo import ZoneInfo

# inherits from db.Model and UserMixin to create a user model for the database
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(100), nullable=False)
    surname = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    contact_number = db.Column(db.String(20), nullable=False)
    street_address = db.Column(db.String(200), nullable=False)

# an event is a single film screening created by a user (the organiser)
class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(150), nullable=False)
    synopsis = db.Column(db.Text, nullable=False)
    poster_image = db.Column(db.String(300))  # optional, just a URL to an image
    classification = db.Column(db.String(10), nullable=False)  # G, PG, M, MA15+, R18+
    runtime = db.Column(db.Integer, nullable=False)  # length in minutes
    screening_format = db.Column(db.String(30))  # e.g. Digital, 35mm

    event_date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)

    ticket_price = db.Column(db.Numeric(6, 2), nullable=False)
    tickets_available = db.Column(db.Integer, nullable=False)
    tickets_remaining = db.Column(db.Integer, nullable=False)

    # one of: Open, Inactive, Sold Out, Cancelled
    # only the application changes this, never the user directly
    status = db.Column(db.String(20), nullable=False, default='Open')

    # acknowledgement of country: none, generic or enhanced
    # text is only stored when the enhanced option is selected
    acknowledgement_type = db.Column(db.String(20), nullable=False, default='generic')
    acknowledgement_text = db.Column(db.Text)

    # foreign keys linking each event to its venue, category and organiser
    venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    organiser_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    created_on = db.Column(db.DateTime, default=datetime.utcnow)

    # relationships let us write event.venue.name instead of doing a manual query
    # backref also lets us go the other way, e.g. venue.events
    venue = db.relationship('Venue', backref='events')
    category = db.relationship('Category', backref='events')
    organiser = db.relationship('User', backref='events')

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    content = db.Column(db.Text, nullable=False)
    posted_on = db.Column(db.DateTime, default=lambda: datetime.now(ZoneInfo("Australia/Brisbane")))
    
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
    created_on_local = db.Column(db.DateTime, default=lambda: datetime.now(ZoneInfo("Australia/Brisbane")))

    event = db.relationship('Event', backref='orders')
    user = db.relationship('User', backref='orders')

# lookup table for the categories shown on the event creation form
class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

# venues are their own table so multiple events can share the same venue
class Venue(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(200), nullable=False)