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

@main.route('/')
def index():
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    else:
        return render_template("index.html") 

@main.route('/transactions', methods=['GET', 'POST'])
@login_required
def transactions():
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    else:
        return render_template("transactions.html")

@main.route('/howto')
def howto():
    return render_template("howto.html")

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