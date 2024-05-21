from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, TextAreaField, SubmitField
from wtforms.validators import DataRequired

class TaxRecordForm(FlaskForm):
    user_id = StringField('User ID', validators=[DataRequired()])
    encrypted_record = TextAreaField('Encrypted Record', validators=[DataRequired()])
    submit = SubmitField('Submit')

class UserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    role = SelectField('Role', choices=[('User', 'User'), ('Staff', 'Staff')], validators=[DataRequired()])
    submit = SubmitField('Submit')
