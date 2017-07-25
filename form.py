from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import Required


class LoginForm(FlaskForm):
    username = StringField('Your username', validators=[Required()])
    password = PasswordField('Your password', validators=[Required()])
    submit = SubmitField('Sign In')