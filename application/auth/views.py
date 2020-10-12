from flask import render_template, redirect, request, url_for, flash
from flask_login import login_user, logout_user, login_required 
from . import auth
from ..models import User, Category
from .forms import LoginForm, RegistrationForm
from .. import db

@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit(): 
        user = User.query.filter_by(username=form.username.data).first()
        if user is not None and user.verify_password(form.password.data): 
            login_user(user, form.remember_me.data) 
            flash("logged in successfully as {}".format(user.username))
            next = request.args.get('next') 
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
        user_info = User.query.filter_by(email=form.email.data).first()
        inflow = Category(name='Inflow', amount=0, user_id=user_info.user_id)
        db.session.add(inflow)
        db.session.commit()
        flash('You can now login')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)

## TO DO: add user email confirmation
