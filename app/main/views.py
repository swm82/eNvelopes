from datetime import datetime
from flask import Flask, render_template, session, redirect, url_for, request
from flask_login import current_user
from . import main
from .. import db
from .forms import AddCategoryForm, AddTransactionForm, AddToCategoryForm, DeleteTransactionForm
from ..models import User, Category, Transaction, Payee
from sqlalchemy import func
from decimal import Decimal

@main.route('/', methods = ['POST', 'GET'])
def index():
    add_category_form = AddCategoryForm()
    add_to_category_form = AddToCategoryForm()
    if request.method == 'POST':
        user = current_user.get_id()
        # If post request is from add_category form, add category to db
        if request.form.get('submit') == 'add_category' and add_category_form.validate_on_submit():
            category = Category(name=add_category_form.category_name.data, amount=0, user_id=current_user.get_id())
            db.session.add(category)
            db.session.commit()
        # If post request is from add_to_category adjust amount in category in db
        if request.form.get('submit') == 'add_to_category' and add_to_category_form.validate_on_submit():
            category = Category.query.filter_by(id=add_to_category_form.category_id.data).first()
            category.amount = category.amount + add_to_category_form.amount.data
            db.session.commit()
            # TODO add remove cash option
            # add delete category option
        return redirect(url_for('main.index'))
    else:
        if not current_user.is_authenticated:
            return redirect(url_for('auth.register'))
        else:
            user = current_user.get_id()
            user_data = User.query.filter_by(id=user).first()
            categories = Category.query.filter_by(user_id=user).all()
            categorized_cash_total = db.session.query(func.sum(Category.amount)).filter_by(user_id=user).scalar()
            if not categorized_cash_total:
                categorized_cash_total = 0
            return render_template("index.html", categories=categories, unbudgeted_amount=user_data.cash-categorized_cash_total, add_category_form=add_category_form, add_to_category_form=add_to_category_form)

# add login required
@main.route('/transactions', methods=['GET', 'POST'])
def transactions():
    add_transaction_form = AddTransactionForm()
    delete_transaction_form = DeleteTransactionForm()
    # Get categories associated with user, pass to form select field, get list of names to utilize in transaction list
    categories = Category.query.filter_by(user_id=current_user.get_id()).all()
    user_category_names = [category.name for category in categories]
    add_transaction_form.category.choices = user_category_names
    if request.method == 'POST':
        if request.form.get('submit') == 'add_transaction' and add_transaction_form.validate_on_submit():
            transaction_amount = add_transaction_form.amount.data
            # Get category from db
            transaction_category = Category.query.filter_by(name=add_transaction_form.category.data).join(User).filter_by(id=current_user.get_id()).first()
            #TODO Transaction must apply amount changes to total money, category amount
            payee = Payee.query.filter_by(name=add_transaction_form.payee.data).join(User).filter_by(id = current_user.get_id()).first()
            # Check if payee exists for user, if not, create new payee with input name for user
            if payee is None:
                payee = Payee(name=add_transaction_form.payee.data, user_id=current_user.get_id())
                db.session.add(payee)
                db.session.commit()
            # Get payee ID from db, create new transaction associated with user, payee, category
            payee = Payee.query.filter_by(name=add_transaction_form.payee.data).join(User).filter_by(id = current_user.get_id()).first()
            transaction = Transaction(user_id=current_user.get_id(), payee_id=payee.id, category_id=transaction_category.id, amount=transaction_amount)
            db.session.add(transaction)
            transactions = Transaction.query.all()
            # Update user's cash
            user_data = User.query.filter_by(id=current_user.get_id()).first()
            user_data.cash = user_data.cash - transaction_amount
            # Update category amount
            transaction_category.amount = transaction_category.amount - transaction_amount
            db.session.commit()
        if request.form.get('submit') == 'delete_transaction' and delete_transaction_form.validate_on_submit():
            # Find and delete transaction
            transaction_to_delete = Transaction.query.filter_by(id=delete_transaction_form.transaction_id.data).first()
            # Get category entry and update amount
            transaction_category = Category.query.filter_by(id=delete_transaction_form.category_id.data).first()
            # Look into decimal conversion, or convert money to ints
            transaction_category.amount = transaction_category.amount + Decimal(delete_transaction_form.transaction_amount.data)
            # Add cash back to user's total
            user_data = User.query.filter_by(id=current_user.get_id()).first()
            user_data.cash = user_data.cash + Decimal(delete_transaction_form.transaction_amount.data)
            db.session.delete(transaction_to_delete)
            db.session.commit()
        return redirect(url_for('main.transactions'))

    else:
        # If Get request, get current transactions, send to Jinja for formatting.  Add line for new transaction
        # TODO - sort in reverse by date, place new transaction at top
        transactions = Transaction.query.join(User).filter_by(id=current_user.get_id()).all()
        return render_template("transactions.html", add_transaction_form=add_transaction_form, delete_transaction_form=delete_transaction_form, transactions=transactions, category_names=user_category_names)