from flask import Blueprint, flash, render_template, request, url_for, redirect
from flask_bcrypt import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user
from .models import User
from .forms import LoginForm, RegisterForm
from . import db

# blueprint that handles authentication routes and views
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm()
    error = None

    # only process the form if it has been submitted and validated
    if login_form.validate_on_submit():
        email = login_form.email.data
        password = login_form.password.data

        # look up the user in the database by email
        user = db.session.scalar(db.select(User).where(User.email==email))

        # two checks. if user is None, then email is incorrect, if password doesn't match the hash, then password is incorrect.
        if user is None:
            error = 'Incorrect email'
        elif not check_password_hash(user.password_hash, password): # takes the hash and cleartext password
            error = 'Incorrect password'

        #if there are no errors, log the user in and redirect to the next page or index
        if error is None:
            login_user(user)
            flash('Logged in successfully')
            nextp = request.args.get('next') 
            if nextp is None or not nextp.startswith('/'):
                return redirect(url_for('main.index'))
            return redirect(nextp)

        # show the error message if there was an error
        else:
            flash(error)
    return render_template('user.html', form=login_form, heading='Login')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out')
    return redirect(url_for('main.index'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    register_form = RegisterForm()

    if register_form.validate_on_submit():
        email = register_form.email.data

        # check if the email already exists in the database
        existing = db.session.scalar(db.select(User).where(User.email == email))
        if existing:
            flash('Email already registered, please log in')
            return redirect(url_for('auth.register'))

        # hash the password
        pwd_hash = generate_password_hash(register_form.password.data).decode('utf-8')

        # create a new user object with the form data and hashed password
        new_user = User(
            firstname=register_form.firstname.data,
            surname=register_form.surname.data,
            email=email,
            contact_number=register_form.contact_number.data,
            street_address=register_form.street_address.data,
            password_hash=pwd_hash
        )

        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful, please log in')
        return redirect(url_for('auth.login'))

    return render_template('user.html', form=register_form, heading='Register')
