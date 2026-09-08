from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from . import db
from .models import Event, Venue, Category
from .forms import EventForm

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    return '<h1>Starter code for assignment 3<h1>'


@main_bp.route('/event/create', methods=['GET', 'POST'])
@login_required
def create_event():
    form = EventForm()

    if form.validate_on_submit():
        venue = Venue.query.filter_by(name=form.venue_name.data).first()
        if venue is None:
            venue = Venue(name=form.venue_name.data, address=form.venue_address.data)
            db.session.add(venue)
            db.session.flush()

        new_event = Event(
            title=form.title.data,
            synopsis=form.synopsis.data,
            poster_image=form.poster_image.data,
            classification=form.classification.data,
            runtime=form.runtime.data,
            screening_format=form.screening_format.data,
            venue_id=venue.id,
            event_date=form.event_date.data,
            start_time=form.start_time.data,
            end_time=form.end_time.data,
            ticket_price=form.ticket_price.data,
            tickets_available=form.tickets_available.data,
            tickets_remaining=form.tickets_available.data,
            acknowledgement_type=form.acknowledgement_type.data,
            category_id=form.category.data,
            organiser_id=current_user.id,
            status='Open',
        )
        db.session.add(new_event)
        db.session.commit()

        flash('Event published successfully.', 'success')
        return redirect(url_for('main.index'))

    return render_template('create_event.html', form=form)