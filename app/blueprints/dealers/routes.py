from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from ...extensions import db
from ...models import Dealer
from ...forms.dealers import DealerForm, DeleteDealerForm

dealers_bp = Blueprint("dealers", __name__)

@dealers_bp.route("/", methods=["GET"])
@login_required
def list_():
    q = request.args.get("q", "").strip()
    query = Dealer.query
    if q:
        query = query.filter(Dealer.razao_social.ilike(f"%{q}%"))
    dealers = query.order_by(Dealer.created_at.desc()).all()
    delete_forms = {d.id: DeleteDealerForm() for d in dealers}
    return render_template("dealers/list.html", dealers=dealers, q=q, delete_forms=delete_forms)


@dealers_bp.route("/novo", methods=["GET", "POST"])
@login_required
def create():
    form = DealerForm()
    if form.validate_on_submit():
        d = Dealer(
            razao_social=form.razao_social.data.strip(),
            endereco=form.endereco.data.strip(),
            cnpj=form.cnpj.data,
            representante_nome=form.representante_nome.data,
            representante_email=form.representante_email.data,
            representante_telefone=form.representante_telefone.data,
            representante_funcao=form.representante_funcao.data,
        )
        db.session.add(d)
        db.session.commit()
        flash("Concessionário salvo.", "success")
        return redirect(url_for("dealers.list_"))
    return render_template("dealers/form.html", form=form, mode="create")


@dealers_bp.route("/<int:dealer_id>/editar", methods=["GET", "POST"])
@login_required
def edit(dealer_id):
    d = Dealer.query.get_or_404(dealer_id)
    form = DealerForm(obj=d)
    if form.validate_on_submit():
        form.populate_obj(d)
        db.session.commit()
        flash("Concessionário atualizado.", "success")
        return redirect(url_for("dealers.list_"))
    return render_template("dealers/form.html", form=form, mode="edit", dealer=d)


@dealers_bp.route("/<int:dealer_id>/excluir", methods=["POST"])
@login_required
def delete(dealer_id):
    d = Dealer.query.get_or_404(dealer_id)
    form = DeleteDealerForm()
    if form.validate_on_submit():
        try:
            db.session.delete(d)
            db.session.commit()
            flash("Concessionário excluído com sucesso.", "success")
            return redirect(url_for("dealers.list_"))
        except:
            flash("Erro ao processar o formulário. Tente novamente.", "danger")
            db.session.rollback()
    return redirect(url_for("dealers.list_"))