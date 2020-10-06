from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, SubmitField, SelectField, HiddenField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo
from wtforms import ValidationError
from .. models import Category

class AddCategoryForm(FlaskForm):
    category_name = StringField('Category Name:', validators=[DataRequired(), Length(1,64)])
    submit = SubmitField('Add Category')

class AddTransactionForm(FlaskForm):
    # Implement category as dropdown of category options
    category = SelectField(validators=[DataRequired()])
    payee = StringField(validators=[DataRequired(), Length(1,64)])
    amount = DecimalField(validators=[DataRequired()], places=2, rounding=None, use_locale=False, number_format=None)
    submit = SubmitField('Add Transaction')

class AddToCategoryForm(FlaskForm):
    amount = DecimalField(validators=[DataRequired()], places=2, rounding=None, use_locale=False, number_format=None)
    category_id = HiddenField()
    submit = SubmitField('Add to Envelope')

class DeleteTransactionForm(FlaskForm):
    transaction_id = HiddenField()
    category_id = HiddenField()
    transaction_amount = HiddenField()
    delete = SubmitField('Delete Transaction')