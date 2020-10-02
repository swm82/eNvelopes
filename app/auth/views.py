from flask import render_template, redirect, request, url_for, flash
from flask_login import login_user, logout_user, login_required 
from . import auth
from ..models import User
from .forms import LoginForm, RegistrationForm
from .. import db

@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit(): # Checksthat request is POST and if valid - combines is_submitted() and validate()
        user = User.query.filter_by(username=form.username.data).first()
        if user is not None and user.verify_password(form.password.data): ## *** VERIFY PASSWORD isn't workign.. obv
            login_user(user, form.remember_me.data) # returns true if success
            next = request.args.get('next') # Determines where the user should be redirected after login
            # if not is_safe_url(next):  *** DEAD FUNCTION?? ****
            #     return flask.abort(400)
            if next is None or not next.startswith('/'):
                next = url_for('main.index')
            return redirect(next)
        flash('Invalid username or password.')
    return render_template('auth/login.html', form=form)

@auth.route('/logout')
@login_required
def logout():
    logout_user() # Flask-Login function removes/resets user session
    flash('You have been logged out.')
    return redirect(url_for('main.index'))

@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data, username=form.username.data, password=form.password.data, role=2, cash=0)
        db.session.add(user)
        db.session.commit()
        flash('You can now login')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)

## TO DO: add user email confirmation
