import os
import uuid

from flask import Blueprint, render_template, redirect, url_for, flash, abort, request, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from . import db
from .models import Event, Venue, Category, Order, Comment
from .forms import EventForm, CommentForm, OrderForm
from markupsafe import Markup, escape


main_bp = Blueprint('main', __name__)

def save_poster_upload(upload):
    """Save an uploaded poster file and return its URL path."""
    filename = f"{uuid.uuid4().hex[:8]}_{secure_filename(upload.filename)}"
    upload_dir = os.path.join(current_app.root_path, 'static', 'img', 'uploads')
    os.makedirs(upload_dir, exist_ok=True)
    upload.save(os.path.join(upload_dir, filename))
    return f"/static/img/uploads/{filename}"

@main_bp.route('/')
def index():
    title = request.args.get('title', '').strip()
    category = request.args.get('category', '').strip()
    sort = request.args.get('sort', 'newest')

    events = Event.query

    if title:
        events = events.filter(
            Event.title.ilike(f'%{title}%')
        )

    if category:
        events = events.join(Event.category).filter(
            Category.name == category
        )

    if sort == 'price_asc':
        events = events.order_by(Event.ticket_price.asc())

    elif sort == 'price_desc':
        events = events.order_by(Event.ticket_price.desc())

    elif sort == 'title_asc':
        events = events.order_by(Event.title.asc())

    else:
        events = events.order_by(Event.event_date.desc())

    events = events.all()

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

        # an uploaded file beats a pasted URL if both are given
        poster = form.poster_image.data
        if form.poster_upload.data:
            poster = save_poster_upload(form.poster_upload.data)

        new_event = Event(
            title=form.title.data,
            synopsis=form.synopsis.data,
            poster_image=poster,
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


@main_bp.route('/event/<int:event_id>')
def event_details(event_id):
    event = Event.query.get_or_404(event_id)

    comment_form = CommentForm() if current_user.is_authenticated else None
    booking_form = OrderForm() if current_user.is_authenticated else None

    return render_template('event_details.html', event=event, comment_form=comment_form, booking_form=booking_form)

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
        if form.poster_upload.data:
            event.poster_image = save_poster_upload(form.poster_upload.data)
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

@main_bp.route('/event/<int:event_id>/comment', methods=['POST'])
@login_required
def comment_event(event_id):
    event = Event.query.get_or_404(event_id)

    form = CommentForm()

    if form.validate_on_submit():
        new_comment = Comment(
            content=form.content.data,
            event_id=event_id,
            user_id=current_user.id,
        )

        db.session.add(new_comment)
        db.session.commit()
        flash('Comment Posted Successfully!', 'success')

    
    return redirect(url_for('main.event_details', event_id=event.id))

@main_bp.route('/event/<int:event_id>/book', methods=['POST'])
@login_required
def book_event(event_id):
    event = Event.query.get_or_404(event_id)

    form = OrderForm()

    if form.validate_on_submit():
        if event.status != 'Open':
            flash('This event is not open for bookings.', 'danger')
            return redirect(url_for('main.event_details', event_id=event.id))

        remaining_tickets = event.tickets_remaining - form.quantity.data
        if remaining_tickets < 0:
            message = Markup("<strong>Order cannot be placed.</strong> You requested more tickets than are available for this session.")
            flash(message, 'danger')
        else:
            event.tickets_remaining = remaining_tickets
            if remaining_tickets == 0:
                event.status = 'Sold Out'

            new_order = Order(
                quantity=form.quantity.data,
                event_id=event_id,
                user_id=current_user.id,
            )
            db.session.add(new_order)
            db.session.commit()

            message = Markup("<strong>Booking confirmed!</strong> Order #{} - {} tickets for {}. A confirmation has been sent to your email.").format(new_order.id, new_order.quantity, escape(event.title))
            flash(message, 'success')

    return redirect(url_for('main.event_details', event_id=event.id))



@main_bp.route('/account/bookings')
@login_required
def my_bookings():
    orders = Order.query.filter_by(user_id=current_user.id).all()
    return render_template('bookings.html', orders=orders)



@main_bp.route('/account/bookings/<int:order_id>/cancel', methods=['POST'])
@login_required
def cancel_booking(order_id):
    order = Order.query.get_or_404(order_id)
    if order.user_id != current_user.id:
        abort(403)
    event = order.event
    if event.status != 'Cancelled':
        event.tickets_remaining += order.quantity
        if event.status == 'Sold Out':
            event.status = 'Open'
    db.session.delete(order)
    db.session.commit()
    flash('Booking cancelled - {} ticket(s) returned for {}.'.format(order.quantity, event.title), 'info')
    return redirect(url_for('main.my_bookings'))