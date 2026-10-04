from datetime import date

from flask_wtf import FlaskForm
from wtforms.fields import (
    SubmitField, StringField, PasswordField, TextAreaField,
    SelectField, IntegerField, FloatField, DateField, TimeField, RadioField
)
from wtforms.validators import (
    InputRequired, Length, Email, EqualTo, NumberRange, Optional
)

# creates the login information
class LoginForm(FlaskForm):
    email = StringField("Email", validators=[InputRequired('Enter email address')])
    password = PasswordField("Password", validators=[InputRequired('Enter user password')])
    submit = SubmitField("Login")

 # this is the registration form
class RegisterForm(FlaskForm):
    firstname = StringField("First Name", validators=[InputRequired()])
    surname = StringField("Surname", validators=[InputRequired()])
    email = StringField("Email Address", validators=[InputRequired(), Email("Please enter a valid email")])
    contact_number = StringField("Contact Number", validators=[InputRequired()])
    street_address = StringField("Street Address", validators=[InputRequired()])

    # linking two fields - password should be equal to data entered in confirm
    password = PasswordField("Password", validators=[InputRequired(),
                  EqualTo('confirm', message="Passwords should match")])
    confirm = PasswordField("Confirm Password", validators=[InputRequired()])

    # submit button
    submit = SubmitField("Register")

class EventForm(FlaskForm):
    title = StringField('Film title', validators=[InputRequired(), Length(max=150)])
    classification = SelectField(
        'Classification',
        choices=[('', 'Select...'), ('G', 'G'), ('PG', 'PG'), ('M', 'M'),
                 ('MA15+', 'MA15+'), ('R18+', 'R18+')],
        validators=[InputRequired()]
    )
    synopsis = TextAreaField('Synopsis', validators=[InputRequired(), Length(max=2000)])
    runtime = IntegerField('Runtime (minutes)', validators=[InputRequired(), NumberRange(min=1)])
    screening_format = SelectField(
        'Screening format',
        choices=[('Digital', 'Digital'), ('35mm', '35mm'), ("Director's Cut", "Director's Cut")]
    )
    category = SelectField('Category', coerce=int, validators=[InputRequired()])
    poster_image = StringField('Poster image URL', validators=[Optional(), Length(max=300)])

    venue_name = StringField('Venue name', validators=[InputRequired(), Length(max=100)])
    venue_address = StringField('Venue address', validators=[InputRequired(), Length(max=200)])
    event_date = DateField('Date', validators=[InputRequired()])
    start_time = TimeField('Start time', validators=[InputRequired()])
    end_time = TimeField('End time', validators=[InputRequired()])

    ticket_price = FloatField('Ticket price ($)', validators=[InputRequired(), NumberRange(min=0)])
    tickets_available = IntegerField('Tickets available', validators=[InputRequired(), NumberRange(min=1)])

    acknowledgement_type = RadioField(
        'Acknowledgement of Country',
        choices=[('none', 'No Acknowledgement'),
                 ('generic', 'Generic Acknowledgement'),
                 ('enhanced', 'Enhanced Acknowledgement')],
        default='generic',
        validators=[InputRequired()]
    )

    # Acknowledgement of Country guidance informed by:
    # - Reconciliation Australia's protocol guidance on Acknowledgement of Country
    # - AIATSIS Map of Indigenous Australia (aiatsis.gov.au/explore/map-indigenous-australia)
    # - Shelley Reys, "Deliver an Acknowledgement of Country that really means
    #   something" (TEDxSydney) — linked in the A2 brief
    acknowledgement_text = TextAreaField(
        'Your Enhanced Acknowledgement (only used if "Enhanced" is selected above)',
        validators=[Optional(), Length(max=1500)]
    )

    submit = SubmitField('Publish Event')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from .models import Category
        self.category.choices = [(c.id, c.name) for c in Category.query.order_by('name')]

    def validate(self, extra_validators=None):
        if not super().validate(extra_validators=extra_validators):
            return False

        # event date must be in the future (per brief FAQ)
        if self.event_date.data and self.event_date.data < date.today():
            self.event_date.errors.append('Event date must be in the future.')
            return False

        if self.acknowledgement_type.data == 'enhanced':
            word_count = len(self.acknowledgement_text.data.split()) if self.acknowledgement_text.data else 0
            if word_count < 40:
                self.acknowledgement_text.errors.append(
                    'An Enhanced Acknowledgement needs at least 40 words — '
                    'this is meant to reflect real research, not a copied line.'
                )
                return False

        return True