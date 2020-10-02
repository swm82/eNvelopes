import os
from datetime import datetime
from flask import Flask, render_template, session, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
## FORM STUFF ##
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired

## Configure Database, app
basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config['SECRET_KEY'] = 'test_String' ## FOR WTFORMS - update to use an env. variable
app.config['SQLALCHEMY_DATABASE_URI'] ='sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Database config

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    username = db.Column(db.String(24), unique=True, nullable=False)
    role = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(40))
    password = db.Column(db.String(24))
    cash = db.Column(db.Numeric) ## THINK ABOUT THIS ONE
    transactions = db.relationship('Transaction', backref='user_transactions')
    categories = db.relationship('Category', backref='user_categories')

    def __repr__(self):
        return '<User %r>' %self.name

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(20), unique=True, nullable=False)
    users = db.relationship('User', backref='user_role')

    def __repr__(self):
        return '<Role %r>' % self.name

class Transaction(db.Model):
    __tablename__ = 'transactions'
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
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    amount = db.Column(db.Numeric, nullable=False)
    db.relationship('Transaction', backref='category')

    def __repr__(self):
        return '<Category %r>' %self.name

class Payee(db.Model):
    __tablename__ = 'payees'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    transactions = db.relationship('Transaction', backref='payee')

    def __repr__(self):
        return '<Payee %r>' %self.name

## FORMS ##

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Submit')


@app.route('/')
def index():
    return render_template("index.html");

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html")


@app.errorhandler(500)
def page_not_found(e):
    return render_template("500.html")

@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, Role=Role, Transaction=Transaction, Category=Category, Payee=Payee)

bootstrap = Bootstrap(app)
moment = Moment(app)
migrate = Migrate(app, db)