from datetime import datetime
from flask import Flask, render_template, session, redirect, url_for, request
from flask_login import current_user
from . import main
from .. import db
from .forms import AddCategoryForm, AddTransactionForm
from ..models import User, Category, Transaction, Payee

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
    # Get categories associated with user, pass to form select field
    categories = Category.query.filter_by(user_id=current_user.get_id()).all()
    # TODO: optimize so the category name holds/hides the id of the category for quick update?
    form.category.choices = [category.name for category in categories]
    if request.method == 'POST':
        if form.validate_on_submit():
            category = form.category.data
            amount = form.amount.data
            print(current_user.get_id())
            q = Category.query.join(User).filter_by(id=current_user.get_id()).first()
            print(q.id)
            #TODO Transaction must apply amount changes to total money, category amount
            #TODO filter the payee query by payee (query payee joined with user to match) - filter the payee match
            payee = Payee.query.filter_by(name=form.payee.data).join(User).filter_by(id = current_user.get_id()).first()
            print(payee)
            if payee is None:
                payee = Payee(name=form.payee.data, user_id=current_user.get_id())
                db.session.add(payee)
                db.session.commit
                print("here")
            else:
                payee = Payee.query.join(User).filter_by
            transaction = Transaction(user_id=current_user.get_id(), payee=payee, category_id=q.id, amount=amount)
            db.session.add(transaction)
            db.session.commit
        return render_template("transactions.html", form=form)
    else:
        return render_template("transactions.html", form=form)