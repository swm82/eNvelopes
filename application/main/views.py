from datetime import datetime
from flask import Flask, abort, render_template, session, redirect, url_for, request, jsonify
from flask_login import current_user, login_required
from . import main
from .. import db
from .forms import AddCategoryForm, AddTransactionForm, AddToCategoryForm, DeleteTransactionForm, DeleteCategoryForm, MoveToCategoryForm
from ..models import User, Category, Transaction, Payee
from sqlalchemy import func
from .utils.helpers import decimal_to_int, format_currency
from .utils.queries import get_categories

def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()
    
@main.route('/shutdown', methods=['GET'])
def shutdown():
    shutdown_server()
    return 'Server shutting down...'


# @main.route('/delete_category', methods = ['POST'])
# def delete_category():
#     DeleteCategoryForm(request.form).validate_on_submit()
#     category = request.form.get('category_id')
#     category = Category.query.filter_by(category_id=category).first()
#     user_inflow = Category.query.filter_by(user_id=current_user.get_id(), name='Inflow').first()
#     user_inflow.amount = user_inflow.amount + category.amount
#     db.session.delete(category)
#     db.session.commit()
#     return redirect(url_for('main.index'))

# @main.route('/add_category', methods=['POST'])
# def add_category():
#     AddCategoryForm(request.form).validate_on_submit()
#     name = request.form.get('category_name')
#     category = Category(name=name, amount=0, user_id=current_user.get_id())
#     db.session.add(category)
#     db.session.commit()
#     return redirect(url_for('main.index'))

# @main.route('/move_to_category', methods=['POST'])
# def move_to_category():
#     MoveToCategoryForm(request.form).validate_on_submit()
    # to_category = Category.query.filter_by(category_id=user_categories[move_to_category_form.to_categories.data]).join(User).filter_by(user_id=current_user.get_id()).first()
    # to_category.amount = to_category.amount + decimal_to_int(move_to_category_form.amount.data)
    # from_category = Category.query.filter_by(category_id=move_to_category_form.from_category_id.data).first();
    # from_category.amount = from_category.amount - decimal_to_int(move_to_category_form.amount.data)
    # db.session.commit()

    

@main.route('/')
def index():
    add_category_form = AddCategoryForm()
    add_to_category_form = AddToCategoryForm()
    delete_category_form = DeleteCategoryForm()
    move_to_category_form = MoveToCategoryForm()
    user_categories = Category.query.filter_by(user_id=current_user.get_id()).all()
    user_categories = { category.name : category.category_id for category in user_categories }
    move_to_category_form.to_categories.choices = list(user_categories.keys())
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    else:
        user = current_user.get_id()
        user_data = User.query.filter_by(user_id=user).first()
        user_inflow = Category.query.filter_by(user_id=current_user.get_id(), name='Inflow').first()
        categories = Category.query.filter_by(user_id=user).filter(Category.name.isnot('Inflow')).all()
        unbudgeted = Category.query.filter_by(user_id=user, name="Inflow").first().amount
        return render_template("index.html", categories=categories, unbudgeted_amount=unbudgeted, add_category_form=add_category_form, add_to_category_form=add_to_category_form, delete_category_form=delete_category_form, move_to_category_form=move_to_category_form) 

@main.route('/transactions', methods=['GET', 'POST'])
@login_required
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

@main.route('/api/delete_transaction', methods=['POST'])
def api_delete_transaction():
    if not request.json or not 'transaction_id' in request.json:
        abort(404, description="not a valid transaction") # uses the 404 error template
    trans_id = int(request.json['transaction_id'])
    transaction_to_delete = Transaction.query.filter_by(trans_id=trans_id).first()
    category_id = transaction_to_delete.category_id
    transaction_category = Category.query.filter_by(category_id=category_id).first()
    if transaction_category is None:
        transaction_category = Category.query.filter_by(user_id=current_user.get_id(), name='Inflow').first()
    transaction_category.amount += transaction_to_delete.amount
    user_data = User.query.filter_by(user_id=current_user.get_id()).first()
    user_data.cash = user_data.cash + transaction_to_delete.amount
    db.session.delete(transaction_to_delete)
    db.session.commit()
    return jsonify({'amount': transaction_to_delete.amount})

@main.route('/api/add_transaction', methods=['POST'])
def api_add_transaction():
    print(request.json)
    if not request.json or not 'category' in request.json or not 'amount' in request.json:
        abort(404, description="invalid transaction") # uses the 404 error template
    user = current_user.get_id()
    category = request.json['category']
    amount = decimal_to_int(request.json['amount'])
    category = Category.query.filter_by(category_id=category).first()
    payee = None
    if 'payee_name' in request.json:
        payee_name = request.json['payee_name']
        payee = Payee.query.filter_by(name=payee_name).join(User).filter_by(user_id=user).first()
        if payee is None:
            payee = Payee(name=payee_name, user_id=user)
            db.session.add(payee)
            db.session.commit()
    income = False
    if category.name == 'Inflow':
        amount = amount * -1
        income = True
    user_data = User.query.filter_by(user_id=user).first()
    user_data.cash = user_data.cash - amount
    category.amount = category.amount - amount
    if payee:
        transaction = Transaction(user_id=user, payee_id=payee.payee_id, category_id=category.category_id, amount=amount, inflow=income)
    else:
        transaction = Transaction(user_id=user, category_id=category.category_id, amount=amount, inflow=income)
    db.session.add(transaction)
    db.session.commit()
    return jsonify({'category_id':category.category_id, 'category_amount':category.amount}), 201

@main.route('/api/transactions')
def api_transactions():
    # returns named tuple of (Transaction, Category, Payee)
    results = db.session.query(Transaction, Category, Payee).filter_by(user_id=current_user.get_id()).join(Category, isouter=True).join(Payee, isouter=True).all()
    transactions = []
    for res in results:
        transaction = {}
        transaction['id'] = res.Transaction.trans_id
        transaction['amount'] = res.Transaction.amount
        transaction['time'] = res.Transaction.timestamp
        if res.Category:
            transaction['category_name'] = res.Category.name
            transaction['category_id'] = res.Category.category_id
        if res.Payee:
            transaction['payee_name'] = res.Payee.name
            transaction['payee_id'] = res.Payee.payee_id
        transactions.append(transaction)
    return jsonify(transactions), 201

@main.route('/api/categories')
def api_categories():
    results = Category.query.filter_by(user_id=current_user.get_id()).all()
    categories = { x.category_id: { 'name': x.name, 'amount': x.amount } for x in results }
    return jsonify(categories), 201


@main.route('/howto')
def howto():
    return render_template("howto.html")

#TODO: handle responses with json
@main.route('/api', methods=['GET'])
def api():
    res = Category.query.filter_by(user_id=current_user.get_id()).all()
    categories = [ { 'id': x.category_id, 'name': x.name, 'amount': x.amount } for x in res]
    res = Payee.query.filter_by(user_id=current_user.get_id()).all()
    payees = [{ 'id': x.payee_id, 'name': x.name } for x in res]
    res = Transaction.query.join(Payee).join(User).join(Category).add_columns(Category.name.label('category_name'), Payee.name.label('payee_name')).filter_by(user_id=current_user.get_id()).all()
    transactions =[{'id': x.Transaction.trans_id, 'category': x.category_name, 'amount':x.Transaction.amount, 'payee': x.payee_name, 'time': x.Transaction.timestamp } for x in res]
    data = { 'categories': categories, 'payees': payees, 'transaction': transactions}
    return jsonify(data), 201

@main.route('/api/add_category', methods=['POST'])
def api_add_category():
    if not request.json or not 'name' in request.json:
        abort(404, description="no name provided") # uses the 404 error template
    name = request.json['name']
    # amount = request.json.get('amount', 0) - need to convert val to int
    amount = 0
    user = current_user.get_id()
    category = Category(name=name, amount=amount, user_id=current_user.get_id())
    db.session.add(category)
    db.session.commit()
    category = Category.query.filter_by(user_id=current_user.get_id(), name=name).first()
    print(category.category_id)
    return jsonify({'name': name, 'amount': amount, 'id': category.category_id}), 201

@main.route('/api/delete_category', methods = ['POST'])
def api_delete_category():
    print(request.json)
    if not request.json or not 'id' in request.json:
        abort(404, description="not a valid cateogory") # uses the 404 error template
    cat_id = request.json['id']
    category = Category.query.filter_by(category_id=cat_id).first()
    user_inflow = Category.query.filter_by(user_id=current_user.get_id(), name='Inflow').first()
    user_inflow.amount = user_inflow.amount + category.amount
    db.session.delete(category)
    db.session.commit()
    return jsonify({'amount': category.amount, 'inflow_amount': user_inflow.amount}), 201


@main.route('/api/add_to_category', methods = ['POST'])
def api_add_to_category():
    print(request.json)
    if not request.json or 'amount' not in request.json or 'category_id' not in request.json:
        abort(404, description="invalid request") # uses the 404 error template
    cat_id = request.json['category_id']
    amount = request.json['amount']
    category = Category.query.filter_by(category_id=cat_id).first()
    category.amount = category.amount + decimal_to_int(amount)
    user_inflow = Category.query.filter_by(user_id=current_user.get_id(), name='Inflow').first()
    user_inflow.amount = user_inflow.amount - decimal_to_int(amount)
    db.session.commit()
    return jsonify({'category_amount': category.amount, 'inflow_amount': user_inflow.amount}), 201