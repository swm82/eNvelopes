from . import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from . import login_manager
from flask_login import UserMixin


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    __table_args__ = {'extend_existing': True}
    user_id = db.Column(db.Integer, primary_key=True, nullable=False)
    username = db.Column(db.String(24), unique=True, nullable=False)
    role = db.Column(db.Integer, db.ForeignKey('roles.role_id'), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(40))
    password_hash = db.Column(db.String(24))
    cash = db.Column(db.Integer, default=0, nullable=False) 
    transactions = db.relationship('Transaction', backref='user_transactions')
    categories = db.relationship('Category', backref='user_categories')
    deleted = db.Column(db.Boolean, default=False, nullable=False)

    ## TODO Add role permissions
    ## TODO add __init__ to initialize user roles

    def get_id(self):
        return self.user_id

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
    role_id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(20), unique=True, nullable=False)
    users = db.relationship('User', backref='user_role')

    def __repr__(self):
        return '<Role %r>' % self.name

class Transaction(db.Model):
    __tablename__ = 'transactions'
    __table_args__ = {'extend_existing': True}
    trans_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.category_id'), nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    payee_id = db.Column(db.Integer, db.ForeignKey('payees.payee_id')) 
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    deleted = db.Column(db.Boolean, default=False, nullable=False)
    inflow = db.Column(db.Boolean, default=False, nullable=False)

    def __repr__(self):
        return'<Transaction %r>' %self.id

class Category(db.Model):
    __tablename__ = 'categories'
    __table_args__ = {'extend_existing': True}
    category_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    amount = db.Column(db.Integer, default=0, nullable=False)
    db.relationship('Transaction', backref='category')
    deleted = db.Column(db.Boolean, default=False, nullable=False)

    def __repr__(self):
        return '<Category %r>' %self.name

class Payee(db.Model):
    __tablename__ = 'payees'
    __table_args__ = {'extend_existing': True}
    payee_id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    transactions = db.relationship('Transaction', backref='payee')

    def __repr__(self):
        return '<Payee %r>' %self.name
