# app/forms/stakeholders.py
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length, Optional

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

        if self.tipo.data == 'EXTERNO':
            if not self.client_id.data:
                self.client_id.errors.append('Selecione o Cliente para stakeholder Externo.')
                return False
            if self.position_id.data:
                self.position_id.errors.append('Stakeholder Externo não deve ter Posição.')
                return False

        elif self.tipo.data == 'INTERNO':
            if not self.position_id.data:
                self.position_id.errors.append('Selecione a Posição para stakeholder Interno.')
                return False
            if self.client_id.data:
                self.client_id.errors.append('Stakeholder Interno não deve ter Cliente.')
                return False

        return True
