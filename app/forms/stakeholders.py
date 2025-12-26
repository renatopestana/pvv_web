# app/forms/stakeholders.py
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length, Optional


class DeleteStakeholderForm(FlaskForm):
    submit = SubmitField('Excluir')


class StakeholderForm(FlaskForm):
    name = StringField(
        'Nome',
        validators=[DataRequired(message='Informe o nome do stakeholder.'), Length(max=150)]
    )
    tipo = SelectField(
        'Tipo',
        choices=[('INTERNO', 'Interno'), ('EXTERNO', 'Externo')],
        validators=[DataRequired()]
    )
    # Usaremos 0 como placeholder "— Selecione —"; no backend convertemos 0 -> None
    client_id = SelectField('Cliente', coerce=int, validators=[Optional()])
    position_id = SelectField('Posição (Cargo)', coerce=int, validators=[Optional()])

    submit = SubmitField('Salvar')

    def validate(self, extra_validators=None):
        if not super().validate(extra_validators=extra_validators):
            return False

        tipo = self.tipo.data
        cli  = self.client_id.data
        pos  = self.position_id.data

        # Trata 0 como "não selecionado"
        cli_is_empty = (cli in (None, 0))
        pos_is_empty = (pos in (None, 0))


        if tipo == 'EXTERNO':
            if cli_is_empty:
                self.client_id.errors.append('Selecione o Cliente para stakeholder Externo.')
                return False
            if not pos_is_empty:
                self.position_id.errors.append('Stakeholder Externo não deve ter Posição.')
                return False

        elif tipo == 'INTERNO':
            if pos_is_empty:
                self.position_id.errors.append('Selecione a Posição para stakeholder Interno.')
                return False
            if not cli_is_empty:
                self.client_id.errors.append('Stakeholder Interno não deve ter Cliente.')
                return False

        return True
