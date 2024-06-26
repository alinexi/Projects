from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, SubmitField, FloatField, IntegerField
from wtforms.validators import DataRequired, NumberRange ,Length
from app.models import User  # Add this line

class TaxRecordForm(FlaskForm):
    full_name = StringField('Full Name', validators=[DataRequired()])
    tax_id = StringField('Tax ID', validators=[DataRequired()])
    address = StringField('Address', validators=[DataRequired()])
    city = StringField('City', validators=[DataRequired()])
    state = StringField('State', validators=[DataRequired()])
    postal_code = StringField('Postal Code', validators=[DataRequired()])
    annual_income = StringField('Annual Income', validators=[DataRequired()])
    income_sources = StringField('Income Sources', validators=[DataRequired()])
    deductions = StringField('Deductions', validators=[DataRequired()])
    deduction_details = StringField('Deduction Details', validators=[DataRequired()])
    tax_rate = StringField('Tax Rate (%)', validators=[DataRequired()])
    calculated_tax = StringField('Calculated Tax', validators=[DataRequired()])
    submit = SubmitField('Submit')

class UserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=150)])
    password = PasswordField('Password', validators=[DataRequired()])
    role = SelectField('Role', choices=[('Sysadmin', 'Sysadmin'), ('Staff', 'Staff'), ('User', 'User')], validators=[DataRequired()])
    submit = SubmitField('Create User')
    
class PaymentForm(FlaskForm):
    amount = FloatField('Amount', validators=[DataRequired(), NumberRange(min=0.01, message='Amount must be greater than zero')])
    payment_details = StringField('Payment Details', validators=[DataRequired()])
    submit = SubmitField('Submit')

class InvoiceForm(FlaskForm):
    user_id = SelectField('Username', coerce=int, validators=[DataRequired()])
    encrypted_invoice = StringField('Encrypted Invoice', validators=[DataRequired()])
    signature = StringField('Signature', validators=[DataRequired()])
    amount_due = FloatField('Amount Due', validators=[DataRequired()])
    submit = SubmitField('Submit')

    def __init__(self, *args, **kwargs):
        super(InvoiceForm, self).__init__(*args, **kwargs)
        self.user_id.choices = [(user.id, user.username) for user in User.query.all()]

class SalaryForm(FlaskForm):
    salary = FloatField('Salary', validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField('Set Salary')


class TaxPercentageForm(FlaskForm):
    user_id = IntegerField('User ID', validators=[DataRequired()])
    tax_percentage = FloatField('Tax Percentage', validators=[DataRequired(), NumberRange(min=0, max=100)])
    submit = SubmitField('Set Tax Percentage')

    def __init__(self, *args, **kwargs):
        super(TaxPercentageForm, self).__init__(*args, **kwargs)
        self.user_id.choices = [(user.id, user.username) for user in User.query.all()]
