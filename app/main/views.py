from datetime import datetime
from flask import Flask, render_template, session, redirect, url_for, request
from flask_login import current_user
from . import main
from .. import db
from .forms import AddCategoryForm, AddTransactionForm
from ..models import User, Category, Transaction

@main.route('/', methods = ['POST', 'GET'])
def index():
    form = AddCategoryForm()
    if request.method == 'POST':
        user = current_user.get_id()
        if form.validate_on_submit():
            category = Category(name=form.category_name.data, amount=0, user_id=current_user.get_id())
            db.session.add(category)
            db.session.commit()
            return redirect(url_for('main.index'))
    else:
        if not current_user.is_authenticated:
            return redirect(url_for('auth.register'))
        else:
            user = current_user.get_id()
            userInfo = User.query.filter_by(id=user).first()
            categories = Category.query.filter_by(user_id=user).all()
            return render_template("index.html", categories=categories, form=form)

# add login required
@main.route('/transactions', methods=['GET', 'POST'])
def transactions():
    form = AddTransactionForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            payee = form.payee.data
            category = form.category.data
            amount = form.amount.data
            #TODO Transaction must apply amount changes to total money, category amount
            transaction = Transaction(user=current_user.get_id(), payee=payee, category=category, amount=amount)
            
        return render_template("transactions.html")
    else:
        return render_template("transactions.html", form=form)