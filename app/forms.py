# forms.py

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, SubmitField, FloatField, IntegerField
from wtforms.validators import DataRequired, NumberRange

class TaxPercentageForm(FlaskForm):
    user_id = IntegerField('User ID', validators=[DataRequired()])
    tax_percentage = FloatField('Tax Percentage', validators=[DataRequired()])
    submit = SubmitField('Update Tax Percentage')

class SalaryForm(FlaskForm):
    salary = FloatField('Salary', validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField('Submit')

class PaymentForm(FlaskForm):
    amount = FloatField('Amount', validators=[DataRequired(), NumberRange(min=0.01, message='Amount must be greater than zero')])
    payment_details = StringField('Payment Details', validators=[DataRequired()])
    submit = SubmitField('Submit')

class InvoiceForm(FlaskForm):
    user_id = SelectField('Username', coerce=int, validators=[DataRequired()])
    invoice = StringField('Invoice', validators=[DataRequired()])
    amount_due = FloatField('Amount Due', validators=[DataRequired()])
    submit = SubmitField('Submit')
