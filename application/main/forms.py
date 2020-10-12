from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, SubmitField, SelectField, HiddenField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo
from wtforms import ValidationError
from .. models import Category

class CurrencyField(DecimalField):
    def process_formdata(self, valuelist):
        if valuelist:
            valuelist[0] = valuelist[0].replace(",", "")
        return super(CurrencyField, self).process_formdata(valuelist)

class AddCategoryForm(FlaskForm):
    category_name = StringField('Category Name:', validators=[DataRequired(), Length(1,64)])
    submit = SubmitField('Add Category')

class AddTransactionForm(FlaskForm):
    category = SelectField(validators=[DataRequired()])
    category_id = HiddenField()
    payee = StringField(validators=[DataRequired(), Length(1,64)])
    amount = CurrencyField(validators=[DataRequired()], places=2, rounding=None, use_locale=False, number_format=None)
    submit = SubmitField('Add Transaction')

class AddToCategoryForm(FlaskForm):
    amount = CurrencyField(validators=[DataRequired()], places=2, rounding=None, use_locale=False, number_format=None)
    category_id = HiddenField()
    # to_categories = SelectField('Move to category...')
    to_category_id = HiddenField()
    delete = SubmitField('Delete Category')
    submit = SubmitField('Add')

class DeleteTransactionForm(FlaskForm):
    transaction_id = HiddenField()
    category_id = HiddenField()
    transaction_amount = HiddenField()
    delete = SubmitField('Delete Transaction')

class DeleteCategoryForm(FlaskForm):
    category_id = HiddenField()
    delete = SubmitField('Delete')