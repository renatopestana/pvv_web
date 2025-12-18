# app/forms/statuses.py
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, RadioField, TextAreaField
from wtforms.validators import DataRequired, Optional, Length, Regexp
from wtforms import SelectMultipleField
from wtforms.widgets import ListWidget, CheckboxInput

# Aceita #RGB ou #RRGGBB
HEX_COLOR_RE = r'^#(?:[0-9a-fA-F]{3}){1,2}$'

# Lista fixa de tipos de cadastro onde o status pode ser usado
STATUS_TARGET_CHOICES = [
    ("equipamentos", "Equipamentos"),
    ("feedbacks", "Feedbacks"),
    ("projetos", "Projetos"),
]

# Campo de múltipla seleção com checkboxes
class MultiCheckboxField(SelectMultipleField):
    widget = ListWidget(prefix_label=False)
    option_widget = CheckboxInput()

class StatusForm(FlaskForm):
    nome = StringField(
        "Nome do Status",
        validators=[DataRequired(), Length(max=80)]
    )
    codigo = StringField(
        "Código/Slug",
        validators=[Optional(), Length(max=50)]
    )
    cor = StringField(
        "Cor (HEX)",
        validators=[
            Optional(),
            Regexp(HEX_COLOR_RE, message="Use um HEX válido, ex: #10B981"),
            Length(max=7),
        ],
        render_kw={"type": "color"}  # <input type="color"> retorna #RRGGBB
    )
    descricao = TextAreaField(
        "Descrição",
        validators=[Optional(), Length(max=300)]
    )

    # Tipos de cadastro (checkboxes)
    tipos_cadastro = MultiCheckboxField(
        "Tipo de cadastro",
        choices=STATUS_TARGET_CHOICES,  # reforçado na rota antes da validação
        validators=[Length(min=1, message="Selecione ao menos um tipo")]
    )

    ativo = RadioField(
        "Ativo",
        choices=[("1", "Sim"), ("0", "Não")],
        default="1",
        validators=[DataRequired()]
    )

    submit = SubmitField("Salvar")


class DeleteStatusForm(FlaskForm):
    submit = SubmitField("Excluir")