# app/forms/functional_areas.py
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length


class FunctionalAreaForm(FlaskForm):
    name = StringField(
        'Nome da Área',
        validators=[DataRequired(message='Informe o nome da área funcional.'), Length(max=120)]
    )
    submit = SubmitField('Salvar')


class FunctionalAreaDeleteForm(FlaskForm):
    submit = SubmitField('Excluir')