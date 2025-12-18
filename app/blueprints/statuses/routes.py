# app/blueprints/statuses/routes.py
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required
from sqlalchemy import or_
from ...extensions import db
from ...models import Status
from ...forms.statuses import StatusForm, DeleteStatusForm, STATUS_TARGET_CHOICES

# Assumindo url_prefix='/statuses' ao registrar o blueprint na factory
statuses_bp = Blueprint("statuses", __name__)

def _csv_to_list(csv_value: str) -> list[str]:
    if not csv_value:
        return []
    return [v for v in csv_value.split(",") if v]

def _list_to_csv(values: list[str]) -> str:
    # normaliza, remove duplicados, ordena por consistência
    return ",".join(sorted(set(values or [])))

@statuses_bp.route("/", methods=["GET"])
@login_required
def list_():
    q = (request.args.get("q") or "").strip()
    query = Status.query

    if q:
        like = f"%{q}%"
        clauses = [Status.nome.ilike(like)]
        if hasattr(Status, "codigo"):
            clauses.append(Status.codigo.ilike(like))
        if hasattr(Status, "descricao"):
            clauses.append(Status.descricao.ilike(like))
        query = query.filter(or_(*clauses))

    # ordenação: created_at desc (se existir) senão id desc
    order_col = getattr(Status, "created_at", getattr(Status, "id", None))
    if order_col is not None:
        query = query.order_by(order_col.desc())

    items = query.all()

    # forms de delete por linha (CSRF)
    delete_forms = {s.id: DeleteStatusForm() for s in items}

    # Mapeamento para exibição das tags de "tipo de cadastro"
    label_map = dict(STATUS_TARGET_CHOICES)

    return render_template(
        "statuses/list.html",
        statuses=items,
        q=q,
        delete_forms=delete_forms,
        tipos_label_map=label_map,
        csv_to_list=_csv_to_list,
    )

@statuses_bp.route("/novo", methods=["GET", "POST"])
@login_required
def create():
    form = StatusForm()
    # ⚠️ Importante: definir choices ANTES da validação
    form.tipos_cadastro.choices = STATUS_TARGET_CHOICES

    # Reprocessa no POST para garantir binding com os choices atuais
    if request.method == "POST":
        # Log de depuração (opcional)
        current_app.logger.debug("POST tipos_cadastro=%s", request.form.getlist("tipos_cadastro"))
        form.process(request.form)

    if form.validate_on_submit():
        ativo_val = form.ativo.data == "1"
        s = Status(
            nome=(form.nome.data or "").strip(),
            descricao=form.descricao.data
        )
        if hasattr(Status, "codigo"):
            s.codigo = (form.codigo.data or "").strip() or None
        if hasattr(Status, "cor"):
            s.cor = (form.cor.data or "").strip() or None

        # salvar tipos de cadastro (como CSV)
        if hasattr(Status, "tipos_cadastro"):
            s.tipos_cadastro = _list_to_csv(form.tipos_cadastro.data)

        # ativo/is_active
        if hasattr(Status, "ativo"):
            s.ativo = ativo_val
        elif hasattr(Status, "is_active"):
            s.is_active = ativo_val

        db.session.add(s)
        db.session.commit()
        flash("Status salvo com sucesso.", "success")
        return redirect(url_for("statuses.list_"))

    return render_template("statuses/form.html", form=form, mode="create")

@statuses_bp.route("/<int:status_id>/editar", methods=["GET", "POST"])
@login_required
def edit(status_id):
    s = Status.query.get_or_404(status_id)
    form = StatusForm(obj=s)
    # ⚠️ Reforçar choices ANTES da validação
    form.tipos_cadastro.choices = STATUS_TARGET_CHOICES

    # Ajusta 'ativo' manualmente
    current_active = getattr(s, "ativo", getattr(s, "is_active", True))

    if request.method == "GET":
        # ✅ PREENCHE APENAS NO GET (para não sobrescrever a seleção do usuário no POST)
        form.ativo.data = "1" if current_active else "0"
        if hasattr(s, "tipos_cadastro"):
            form.tipos_cadastro.data = _csv_to_list(getattr(s, "tipos_cadastro", ""))

    if request.method == "POST":
        # Log de depuração (opcional)
        current_app.logger.debug("POST tipos_cadastro=%s", request.form.getlist("tipos_cadastro"))
        # Reprocessa o form para garantir binding com os choices atuais e valores do POST
        form.process(request.form)

    if form.validate_on_submit():
        s.nome = (form.nome.data or "").strip()
        s.descricao = form.descricao.data

        if hasattr(Status, "codigo"):
            s.codigo = (form.codigo.data or "").strip() or None
        if hasattr(Status, "cor"):
            s.cor = (form.cor.data or "").strip() or None

        # atualizar tipos de cadastro
        if hasattr(Status, "tipos_cadastro"):
            s.tipos_cadastro = _list_to_csv(form.tipos_cadastro.data)

        ativo_val = form.ativo.data == "1"
        if hasattr(Status, "ativo"):
            s.ativo = ativo_val
        elif hasattr(Status, "is_active"):
            s.is_active = ativo_val

        db.session.commit()
        flash("Status atualizado.", "success")
        return redirect(url_for("statuses.list_"))

    return render_template("statuses/form.html", form=form, mode="edit", status=s)

@statuses_bp.route("/<int:status_id>/excluir", methods=["POST"])
@login_required
def delete(status_id):
    s = Status.query.get_or_404(status_id)
    form = DeleteStatusForm()
    if form.validate_on_submit():
        try:
            db.session.delete(s)
            db.session.commit()
            flash("Status excluído.", "success")
        except Exception:
            db.session.rollback()
            flash("Não foi possível excluir o status. Verifique vínculos existentes.", "danger")
    else:
        flash("Falha de validação no formulário de exclusão.", "danger")
    return redirect(url_for("statuses.list_"))