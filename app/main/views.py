from datetime import datetime
from flask import Flask, render_template, session, redirect, url_for
from flask_login import current_user
from . import main
from .. import db
from ..models import User, Category

@main.route('/')
def index():
    if not current_user.is_authenticated:
        return redirect(url_for('auth.register'))
    else:
        user = current_user.get_id()
        userInfo = User.query.filter_by(id=user).first()
        categories = Category.query.filter_by(user_id=user).all()
        return render_template("index.html", categories=categories)
    return render_template("index.html");