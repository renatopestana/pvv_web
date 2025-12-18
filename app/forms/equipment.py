from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, SelectField
from wtforms.validators import DataRequired, Optional, Length

class EquipmentForm(FlaskForm):
    name = StringField("Nome do Equipamento (Item)", validators=[DataRequired(), Length(max=180)])
    pn = StringField("PN (Part Number)", validators=[Optional(), Length(max=80)])
    model_number = StringField("Model Number", validators=[Optional(), Length(max=120)])
    serial_number = StringField("Nº de Série", validators=[Optional(), Length(max=120)])
    machine_installed = StringField("Machine Installed", validators=[Optional(), Length(max=180)])
    image_ref = StringField("Imagem de Referência (URL/Path)", validators=[Optional(), Length(max=255)])

    asset_tag = StringField("Patrimônio/Código (opcional)", validators=[Optional(), Length(max=80)])
    category = StringField("Categoria (opcional)", validators=[Optional(), Length(max=120)])
    brand = StringField("Marca (opcional)", validators=[Optional(), Length(max=120)])

    owner_id = SelectField("Owner", coerce=int)
    current_responsible_id = SelectField("Current Responsible", coerce=int)
    location_id = SelectField("Location (Cliente)", coerce=int)
    project_id = SelectField("Projeto", coerce=int)
    status_id = SelectField("Status", coerce=int)

    notes = TextAreaField("Observações", validators=[Optional(), Length(max=5000)])
    submit = SubmitField("Salvar")


class DeleteEquipmentForm(FlaskForm):
    submit = SubmitField("Excluir")