from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Email, Length, EqualTo


class RegisterForm(FlaskForm):
    full_name = StringField('Nome completo', validators=[DataRequired(), Length(max=100)])
    email = StringField('E-mail', validators=[DataRequired(), Email(), Length(max=120)])
    cpf = StringField('CPF', validators=[Length(max=14)])
    password = PasswordField('Senha', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirmar senha', validators=[
        DataRequired(), EqualTo('password', message='As senhas devem coincidir.')
    ])
    submit = SubmitField('Criar conta')


class LoginForm(FlaskForm):
    email = StringField("E-mail", validators=[DataRequired(), Email(), Length(max=255)])
    password = PasswordField("Senha", validators=[DataRequired()])
    remember = BooleanField('Lembrar de mim') 
    submit = SubmitField("Entrar")
