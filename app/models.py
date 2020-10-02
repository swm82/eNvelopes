from . import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from . import login_manager
from flask_login import UserMixin


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    username = db.Column(db.String(24), unique=True, nullable=False)
    role = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(40))
    password_hash = db.Column(db.String(24))
    cash = db.Column(db.Numeric) ## THINK ABOUT THIS ONE
    transactions = db.relationship('Transaction', backref='user_transactions')
    categories = db.relationship('Category', backref='user_categories')

    ## TODO Add role permissions
    ## TODO add __init__ to initialize user roles

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User %r>' %self.name

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class Role(db.Model):
    __tablename__ = 'roles'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(20), unique=True, nullable=False)
    users = db.relationship('User', backref='user_role')

    def __repr__(self):
        return '<Role %r>' % self.name

class Transaction(db.Model):
    __tablename__ = 'transactions'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    amount = db.Column(db.Numeric, nullable=False)
    payee_id = db.Column(db.Integer, db.ForeignKey('payees.id')) 
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return'<Transaction %r>' %self.id

class Category(db.Model):
    __tablename__ = 'categories'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    amount = db.Column(db.Numeric, nullable=False)
    db.relationship('Transaction', backref='category')

    def __repr__(self):
        return '<Category %r>' %self.name

class Payee(db.Model):
    __tablename__ = 'payees'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    transactions = db.relationship('Transaction', backref='payee')

    def __repr__(self):
        return '<Payee %r>' %self.name
