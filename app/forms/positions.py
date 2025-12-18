# app/forms/positions.py
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length

class PositionForm(FlaskForm):
    name = StringField(
        'Nome da Posição (Cargo)',
        validators=[DataRequired(message='Informe o nome da posição.'), Length(max=120)]
    )
    functional_area_id = SelectField(
        'Área Funcional',
        coerce=int,
        validators=[DataRequired(message='Selecione a área funcional.')]
    )
    submit = SubmitField('Salvar')
