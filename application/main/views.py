from datetime import datetime
from flask import Flask, render_template, session, redirect, url_for, request
from flask_login import current_user
from . import main
from .. import db
from .forms import AddCategoryForm, AddTransactionForm, AddToCategoryForm, DeleteTransactionForm, DeleteCategoryForm
from ..models import User, Category, Transaction, Payee
from sqlalchemy import func

@main.route('/', methods = ['POST', 'GET'])
def index():
    add_category_form = AddCategoryForm()
    add_to_category_form = AddToCategoryForm()
    delete_category_form = DeleteCategoryForm()
    if request.method == 'POST':
        user = current_user.get_id()
        # If post request is from add_category form, add category to db
        if add_category_form.submit.data and add_category_form.validate_on_submit():
            category = Category(name=add_category_form.category_name.data, amount=0, user_id=current_user.get_id())
            db.session.add(category)
            db.session.commit()
        # If post request is from add_to_category adjust amount in category in db
        if add_to_category_form.submit.data and add_to_category_form.validate_on_submit():
            category = Category.query.filter_by(category_id=add_to_category_form.category_id.data).first()
            category.amount = category.amount + decimal_to_int(add_to_category_form.amount.data)
            user_inflow = Category.query.filter_by(user_id=current_user.get_id(), name='Inflow').first()
            user_inflow.amount = user_inflow.amount - decimal_to_int(add_to_category_form.amount.data)
            db.session.commit()
        if delete_category_form.delete.data and delete_category_form.validate_on_submit():
            category = Category.query.filter_by(category_id=delete_category_form.category_id.data).first()
            user_inflow = Category.query.filter_by(user_id=current_user.get_id(), name='Inflow').first()
            user_inflow.amount = user_inflow.amount + category.amount
            db.session.delete(category)
            db.session.commit()


        return redirect(url_for('main.index'))
    else:
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        else:
            user = current_user.get_id()
            user_data = User.query.filter_by(user_id=user).first()
            user_inflow = Category.query.filter_by(user_id=current_user.get_id(), name='Inflow').first()
            categories = Category.query.filter_by(user_id=user).filter(Category.name.isnot('Inflow')).all()
            unbudgeted = Category.query.filter_by(user_id=user, name="Inflow").first().amount
            return render_template("index.html", categories=categories, unbudgeted_amount=unbudgeted, add_category_form=add_category_form, add_to_category_form=add_to_category_form, delete_category_form=delete_category_form)

# add login required
@main.route('/transactions', methods=['GET', 'POST'])
def transactions():
    add_transaction_form = AddTransactionForm()
    delete_transaction_form = DeleteTransactionForm()
    # Get categories associated with user, pass to form select field, get list of names to utilize in transaction list
    categories = Category.query.filter_by(user_id=current_user.get_id()).all()
    # Category dict to be used in template
    payees = Payee.query.filter_by(user_id=current_user.get_id()).all()
    payees = { payee.payee_id : payee.name for payee in payees }
    categories = { category.category_id : category.name for category in categories }
    add_transaction_form.category.choices = list(categories.values())
    if request.method == 'POST':
        if request.form.get('submit') == 'add_transaction' and add_transaction_form.validate_on_submit():
            transaction_amount = decimal_to_int(add_transaction_form.amount.data)
            # Get category from db
            payee = Payee.query.filter_by(name=add_transaction_form.payee.data).join(User).filter_by(user_id = current_user.get_id()).first()
            # Check if payee exists for user, if not, create new payee with input name for user
            if payee is None:
                payee = Payee(name=add_transaction_form.payee.data, user_id=current_user.get_id())
                db.session.add(payee)
                db.session.commit()
            # Get payee ID from db, create new transaction associated with user, payee, category
            payee = Payee.query.filter_by(name=add_transaction_form.payee.data).join(User).filter_by(user_id = current_user.get_id()).first()
            # If inflow, add to user, if outflow, subtract from user, update category
            transaction_category = Category.query.filter_by(name=add_transaction_form.category.data).join(User).filter_by(user_id=current_user.get_id()).first()
            income = False
            if add_transaction_form.category.data == 'Inflow':
                transaction_amount = transaction_amount * -1
                income = True
            user_data = User.query.filter_by(user_id=current_user.get_id()).first()
            user_data.cash = user_data.cash - transaction_amount
            transaction_category.amount = transaction_category.amount - transaction_amount
            transaction = Transaction(user_id=current_user.get_id(), payee_id=payee.payee_id, category_id=transaction_category.category_id, amount=transaction_amount, inflow=income)
            db.session.add(transaction)
            # Update category amount
            db.session.commit()
        if request.form.get('submit') == 'delete_transaction' and delete_transaction_form.validate_on_submit():
            # Find and delete transaction
            transaction_to_delete = Transaction.query.filter_by(trans_id=delete_transaction_form.transaction_id.data).first()
            # Get category entry and update amount
            transaction_category = Category.query.filter_by(category_id=delete_transaction_form.category_id.data).first()
            transaction_category.amount = transaction_category.amount + transaction_to_delete.amount
            # Add cash back to user's total
            user_data = User.query.filter_by(user_id=current_user.get_id()).first()
            user_data.cash = user_data.cash + decimal_to_int(delete_transaction_form.transaction_amount.data)
            db.session.delete(transaction_to_delete)
            db.session.commit()
        return redirect(url_for('main.transactions'))

    else:
        # If Get request, get current transactions, send to Jinja for formatting.  Add line for new transaction
        # TODO - sort in reverse by date, place new transaction at top
        transactions = Transaction.query.join(User).filter_by(user_id=current_user.get_id()).all()
        return render_template("transactions.html", add_transaction_form=add_transaction_form, delete_transaction_form=delete_transaction_form, transactions=transactions, category_dict=categories, payee_dict=payees)


# Helper methods - move to seperate pkg
def decimal_to_int(value):
    string_value = str(value)
    if '.' not in string_value:
        return int(string_value) * 100
    parts = string_value.split('.')
    intvalue = int(''.join(parts))
    return intvalue

def format_currency(value):
    return "$" + str(float(value)/100)