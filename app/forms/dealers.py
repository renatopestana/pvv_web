from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, Length

class DealerForm(FlaskForm):
    razao_social = StringField("Razão Social", validators=[DataRequired(), Length(max=180)])
    endereco = TextAreaField("Endereço", validators=[DataRequired(), Length(max=300)])
    cnpj = StringField("CNPJ", validators=[DataRequired(), Length(max=18)])
    representante_nome = StringField("Representante Legal", validators=[DataRequired(), Length(max=180)])
    representante_email = StringField("E-mail do Representante", validators=[DataRequired(), Email(), Length(max=255)])
    representante_telefone = StringField("Telefone do Representante", validators=[DataRequired(), Length(max=30)])
    representante_funcao = StringField("Função/Cargo do Representante", validators=[DataRequired(), Length(max=120)])
    submit = SubmitField("Salvar")

class DeleteDealerForm(FlaskForm):
    submit = SubmitField("Excluir")