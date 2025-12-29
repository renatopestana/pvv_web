from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, RadioField, TextAreaField
from wtforms.validators import DataRequired, Optional, Email, Length

class ClientForm(FlaskForm):
    tipo = RadioField("Tipo de Cliente", choices=[("PF","Pessoa Física"),("PJ","Pessoa Jurídica")], default="PJ", validators=[DataRequired()])
    org_id = StringField('Org ID (Operations Center)', validators=[Optional(), Length(max=64)])

    # Comuns
    nome_razao = StringField("Nome / Razão Social", validators=[DataRequired(), Length(max=180)])
    endereco = TextAreaField("Endereço", validators=[DataRequired(), Length(max=300)])

    # PF
    nacionalidade = StringField("Nacionalidade", validators=[Optional(), Length(max=80)])
    estado_civil = StringField("Estado Civil", validators=[Optional(), Length(max=60)])
    profissao = StringField("Profissão", validators=[Optional(), Length(max=120)])
    rg = StringField("RG", validators=[Optional(), Length(max=30)])
    orgao_emissor_rg = StringField("Órgão Emissor do RG", validators=[Optional(), Length(max=50)])
    cpf = StringField("CPF", validators=[Optional(), Length(max=14)])
    email = StringField("E-mail", validators=[Optional(), Email(), Length(max=255)])
    telefone = StringField("Telefone", validators=[Optional(), Length(max=30)])

    # PJ
    cnpj = StringField("CNPJ", validators=[Optional(), Length(max=18)])
    representante_nome = StringField("Representante Legal", validators=[Optional(), Length(max=180)])
    representante_email = StringField("E-mail do Representante", validators=[Optional(), Email(), Length(max=255)])
    representante_telefone = StringField("Telefone do Representante", validators=[Optional(), Length(max=30)])
    representante_funcao = StringField("Função/Cargo do Representante", validators=[Optional(), Length(max=120)])

    submit = SubmitField("Salvar")


class DeleteClientForm(FlaskForm):
    submit = SubmitField("Excluir")