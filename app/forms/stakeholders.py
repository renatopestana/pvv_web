# app/forms/stakeholders.py
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length, Optional, Email

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
    client_id   = SelectField('Cliente', coerce=int, validators=[Optional()])
    position_id = SelectField('Posição (Cargo)', coerce=int, validators=[Optional()])

    email = StringField('E-mail',  validators=[Optional(), Email(), Length(max=150)])
    phone = StringField('Telefone', validators=[Optional(), Length(max=30)])

    submit = SubmitField('Salvar')

    def validate(self, extra_validators=None):
        if not super().validate(extra_validators=extra_validators):
            return False

        tipo = self.tipo.data
        cli  = self.client_id.data
        pos  = self.position_id.data

        # Trata '0' como "não selecionado"
        cli_is_empty = (cli in (None, 0))
        pos_is_empty = (pos in (None, 0))

        if tipo == 'EXTERNO':
            if cli_is_empty:
                self.client_id.errors.append('Selecione o Cliente para stakeholder Externo.')
                return False
            # cargo é opcional
        elif tipo == 'INTERNO':
            if pos_is_empty:
                self.position_id.errors.append('Selecione a Posição para stakeholder Interno.')
                return False
            # cliente é opcional

        return True
