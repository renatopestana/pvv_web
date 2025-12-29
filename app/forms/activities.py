# app/forms/activities.py
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, SelectField, SelectMultipleField, DateField, FloatField
from wtforms.validators import DataRequired, Optional, Length, NumberRange

class ActivityForm(FlaskForm):
    description = TextAreaField(
        'Descrição da atividade', validators=[DataRequired(message='Informe a descrição.'), Length(max=400)]
    )

    project_id = SelectField('Projeto', coerce=int, validators=[DataRequired(message='Selecione o projeto.')])
    start_date = DateField('Data de início', format='%Y-%m-%d', validators=[DataRequired(message='Informe a data de início.')])
    end_date = DateField('Data de fim', format='%Y-%m-%d', validators=[Optional()])
    duration_hours = FloatField('Duração (horas)', validators=[Optional(), NumberRange(min=0)])
    owner_user_id = SelectField('Responsável (Owner)', coerce=int, validators=[DataRequired(message='Selecione o responsável.')])
    executor_user_id = SelectField('Executor', coerce=int, validators=[DataRequired(message='Selecione o executor.')])

    environment = SelectField(
        'Ambiente',
        choices=[('SIMULADO', 'Simulado'), ('CONTROLADO', 'Controlado'), ('REAL', 'Real')],
        validators=[DataRequired(message='Selecione o ambiente.')]
    )

    client_id = SelectField('Cliente', coerce=int, validators=[Optional()])
    dealer_id = SelectField('Concessionário', coerce=int, validators=[Optional()])
    equipment_ids = SelectMultipleField('Equipamentos', coerce=int, validators=[Optional()])
    machine_serials = SelectMultipleField('Máquinas (VIN/Chassi)', coerce=str, validators=[Optional()])
    status_id = SelectField('Status', coerce=int, validators=[DataRequired(message='Selecione o status.')])
    submit = SubmitField('Salvar')
