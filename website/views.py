from flask import Blueprint, render_template, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from . import db
from .models import Event, Venue, Category, Order
from .forms import EventForm


main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    events = Event.query.order_by(Event.event_date).all()
    return render_template('index.html', events=events)

@main_bp.route('/event/create', methods=['GET', 'POST'])
@login_required  # only logged-in users can create events
def create_event():
    form = EventForm()

    if form.validate_on_submit():
        # reuse the venue if one with this name exists, otherwise create it
        venue = Venue.query.filter_by(name=form.venue_name.data).first()
        if venue is None:
            venue = Venue(name=form.venue_name.data, address=form.venue_address.data)
            db.session.add(venue)
            db.session.flush()  # assigns venue.id so we can use it below

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
            # only keep the text if the enhanced option was actually chosen
            acknowledgement_text=form.acknowledgement_text.data if form.acknowledgement_type.data == 'enhanced' else None,
            category_id=form.category.data,
            organiser_id=current_user.id,
            # new events always start as Open - status is never set by the user
            status='Open',
        )
        db.session.add(new_event)
        db.session.commit()

        flash('Event published successfully.', 'success')
        return redirect(url_for('main.index'))

    return render_template('create_event.html', form=form)


@main_bp.route('/event/<int:event_id>/update', methods=['GET', 'POST'])
@login_required
def update_event(event_id):
    event = Event.query.get_or_404(event_id)

    # only the organiser who created the event may edit it
    if event.organiser_id != current_user.id:
        abort(403)

    form = EventForm(obj=event)  # pre-fill the form with the existing details

    # venue and category need to be filled in manually on the first load
    if not form.is_submitted():
        form.venue_name.data = event.venue.name
        form.venue_address.data = event.venue.address
        form.category.data = event.category_id

    if form.validate_on_submit():
        event.title = form.title.data
        event.synopsis = form.synopsis.data
        event.poster_image = form.poster_image.data
        event.classification = form.classification.data
        event.runtime = form.runtime.data
        event.screening_format = form.screening_format.data
        event.event_date = form.event_date.data
        event.start_time = form.start_time.data
        event.end_time = form.end_time.data
        event.ticket_price = form.ticket_price.data
        event.category_id = form.category.data
        event.acknowledgement_type = form.acknowledgement_type.data
        event.acknowledgement_text = (
            form.acknowledgement_text.data if form.acknowledgement_type.data == 'enhanced' else None
        )

        event.venue.name = form.venue_name.data
        event.venue.address = form.venue_address.data

        db.session.commit()
        flash('Event updated successfully.', 'success')
        return redirect(url_for('main.index'))

    return render_template('create_event.html', form=form, editing=True, event=event)


@main_bp.route('/event/<int:event_id>/cancel', methods=['POST'])
@login_required
def cancel_event(event_id):
    event = Event.query.get_or_404(event_id)

    # only the organiser who created the event may cancel it
    if event.organiser_id != current_user.id:
        abort(403)

    event.status = 'Cancelled'
    db.session.commit()

    flash('Event has been cancelled.', 'info')
    return redirect(url_for('main.index'))

@main_bp.route('/account/bookings')
@login_required
def my_bookings():
    orders = Order.query.filter_by(user_id=current_user.id).all()
    return render_template('bookings.html', orders=orders)