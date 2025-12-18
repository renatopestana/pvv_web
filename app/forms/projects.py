# app/forms/projects.py
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, SelectField
from wtforms.validators import DataRequired, Optional, Length


class ProjectForm(FlaskForm):
    name = StringField("Nome do Projeto", validators=[DataRequired(), Length(max=180)])
    description = TextAreaField("Descrição", validators=[Optional(), Length(max=2000)])

    # NOVO: status apenas para projetos (choices definidas nas rotas)
    status_id = SelectField("Status", coerce=int, validators=[Optional()])

    submit = SubmitField("Salvar")


class DeleteProjectForm(FlaskForm):
    submit = SubmitField("Excluir")