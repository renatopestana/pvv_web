from flask import Blueprint, jsonify, render_template, redirect, url_for, flash, request
from flask_login import login_required
from ...extensions import db
from ...models import Client
from ...forms.clients import ClientForm, DeleteClientForm

clients_bp = Blueprint("clients", __name__)

@clients_bp.route("/", methods=["GET"], endpoint="list")
@login_required
def list_():
    q = request.args.get("q", "").strip()
    query = Client.query
    if q:
        query = query.filter(Client.nome_razao.ilike(f"%{q}%"))
    clients = query.order_by(Client.created_at.desc()).all()
    delete_forms = {c.id: DeleteClientForm() for c in clients}
    return render_template("clients/list.html", clients=clients, q=q, delete_forms=delete_forms)


@clients_bp.get('/<int:id>/org')
@login_required
def client_org(id):
    c = db.session.query(Client).get_or_404(id)
    return jsonify({'org_id': c.org_id or ''})


@clients_bp.route("/novo", methods=["GET", "POST"], endpoint="create")
@login_required
def create():
    form = ClientForm()
    if form.validate_on_submit():
        c = Client(
            tipo=form.tipo.data,
            nome_razao=form.nome_razao.data.strip(),
            org_id=form.org_id.data,
            endereco=form.endereco.data.strip(),
            nacionalidade=form.nacionalidade.data,
            estado_civil=form.estado_civil.data,
            profissao=form.profissao.data,
            rg=form.rg.data,
            orgao_emissor_rg=form.orgao_emissor_rg.data,
            cpf=form.cpf.data,
            email=form.email.data,
            telefone=form.telefone.data,
            cnpj=form.cnpj.data,
            representante_nome=form.representante_nome.data,
            representante_email=form.representante_email.data,
            representante_telefone=form.representante_telefone.data,
            representante_funcao=form.representante_funcao.data,
        )
        db.session.add(c)
        db.session.commit()
        flash("Cliente salvo com sucesso.", "success")
        return redirect(url_for("clients.list"))
    return render_template("clients/form.html", form=form, mode="create")


@clients_bp.route("/<int:client_id>/editar", methods=["GET", "POST"], endpoint="edit")
@login_required
def edit(client_id):
    c = Client.query.get_or_404(client_id)
    form = ClientForm(obj=c)
    if form.validate_on_submit():
        form.populate_obj(c)
        db.session.commit()
        flash("Cliente atualizado.", "success")
        return redirect(url_for("clients.list"))
    return render_template("clients/form.html", form=form, mode="edit", client=c)


@clients_bp.route("/<int:client_id>/excluir", methods=["POST"], endpoint="delete")
@login_required
def delete_(client_id):
    c = Client.query.get_or_404(client_id)
    form = DeleteClientForm()
    if form.validate_on_submit():
        try:
            db.session.delete(c)
            db.session.commit()
            flash("Cliente excluído com sucesso.", "success")
            return redirect(url_for("clients.list"))
        except:
            flash("Erro ao processar o formulário. Tente novamente.", "danger")
            return redirect(url_for("clients.list"))
    else:
        flash("Não foi possível excluir o cliente (falha de validação).", "danger")
    return redirect(url_for("clients.list"))
