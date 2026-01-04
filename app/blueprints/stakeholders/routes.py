
# app/blueprints/stakeholders/routes.py
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required
from sqlalchemy.orm import selectinload
from app.extensions import db
from app.models import Stakeholder, Client, Position
from app.forms.stakeholders import StakeholderForm, DeleteStakeholderForm
from . import bp_stakeholders

# Mantém o helper já existente
def _fill_choices(form):
    # Ordene pelo nome real de banco (nome_razao), não pela property 'name'
    clients = Client.query.order_by(Client.nome_razao.asc()).all()
    positions = Position.query.order_by(Position.name.asc()).all()
    form.client_id.choices = [(0, '— Selecione —')] + [(c.id, c.name) for c in clients]
    form.position_id.choices = [
        (0, '— Selecione —')
    ] + [
        (p.id, f'{p.name} ({p.functional_area.name})') for p in positions
    ]

@bp_stakeholders.route('/')
@login_required
def list():
    # Filtros da querystring
    q      = (request.args.get('q') or '').strip()
    tipo   = (request.args.get('tipo') or '').strip().upper()
    # Converta para int diretamente (melhor do que comparar string vs coluna int)
    client_id   = request.args.get('client_id', type=int)
    position_id = request.args.get('position_id', type=int)

    # Query base + eager load para evitar N+1
    query = (
        Stakeholder.query.options(
            selectinload(Stakeholder.client),
            selectinload(Stakeholder.position).selectinload(Position.functional_area)
        )
    )

    # Texto (nome)
    if q:
        query = query.filter(Stakeholder.name.ilike(f'%{q}%'))

    # Tipo
    if tipo in ('INTERNO', 'EXTERNO'):
        query = query.filter(Stakeholder.tipo == tipo)

    # Filtro condicional (somente quando faz sentido)
    # EXTERNO => filtra por cliente; INTERNO => filtra por cargo (position)
    if tipo == 'EXTERNO' and client_id:
        query = query.filter(Stakeholder.client_id == client_id)
    if tipo == 'INTERNO' and position_id:
        query = query.filter(Stakeholder.position_id == position_id)

    stakeholders = query.order_by(Stakeholder.created_at.desc()).all()

    # Combos da listagem (para preencher os filtros)
    clients   = Client.query.order_by(Client.nome_razao.asc()).all()
    positions = Position.query.order_by(Position.name.asc()).all()

    # Deleção por linha (já estava ok)
    delete_forms = {s.id: DeleteStakeholderForm() for s in stakeholders}

    return render_template(
        'stakeholders/list.html',
        stakeholders=stakeholders,
        q=q,
        tipo=tipo,
        client_id=client_id,
        position_id=position_id,
        clients=clients,
        positions=positions,
        delete_forms=delete_forms,
    )



@bp_stakeholders.route('/new', methods=['GET', 'POST'])
@login_required
def create():
    form = StakeholderForm()
    _fill_choices(form)

    if request.method == 'POST':
        # Para Interno, o campo cliente é oculto no form; garanta que não será aplicado
        if form.tipo.data == 'INTERNO':
            form.client_id.data = 0  # placeholder

    if form.validate_on_submit():
        client_id   = form.client_id.data   if form.client_id.data   != 0 else None
        position_id = form.position_id.data if form.position_id.data != 0 else None

        # >>> ordem segura: relações primeiro; tipo por último
        sh = Stakeholder(
            name=form.name.data.strip()
        )
        sh.email = (form.email.data or '').strip() or None
        sh.phone = (form.phone.data or '').strip() or None

        if form.tipo.data == 'EXTERNO':
            sh.client_id   = client_id            # obrigatório
            sh.position_id = position_id          # opcional
            sh.tipo        = 'EXTERNO'            # por último
        else:  # INTERNO
            sh.position_id = position_id          # obrigatório
            sh.client_id   = None                 # não salvar cliente
            sh.tipo        = 'INTERNO'            # por último

        db.session.add(sh)
        try:
            db.session.commit()
            flash('Stakeholder criado com sucesso!', 'success')
            return redirect(url_for('stakeholders.list'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao salvar: {e}', 'danger')
    else:
        if request.method == 'POST':
            flash(f'Erros no formulário: {form.errors}', 'danger')
    

    return render_template('stakeholders/form.html', form=form, title='Novo Stakeholder')




@bp_stakeholders.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    sh = Stakeholder.query.get_or_404(id)
    form = StakeholderForm(obj=sh)
    _fill_choices(form)

    # GET: coloca 0 quando relação é None (para atender ao placeholder nas choices)
    if request.method == 'GET':
        if sh.client_id is None:
            form.client_id.data = 0
        if sh.position_id is None:
            form.position_id.data = 0

    # NÃO converta 0 -> None ANTES da validação (causa "Not a valid choice")
    if form.validate_on_submit():
        # Normaliza placeholders APÓS validação
        client_id   = form.client_id.data   if form.client_id.data   != 0 else None
        position_id = form.position_id.data if form.position_id.data != 0 else None

        # Campos básicos
        sh.name  = form.name.data.strip()
        sh.email = (form.email.data or '').strip() or None
        sh.phone = (form.phone.data or '').strip() or None

        # Relações primeiro, tipo por último (evita validador do model em estado transitório)
        if form.tipo.data == 'EXTERNO':
            sh.client_id   = client_id        # obrigatório
            sh.position_id = position_id      # opcional
            sh.tipo        = 'EXTERNO'
        else:  # INTERNO
            sh.position_id = position_id      # obrigatório
            sh.client_id   = None             # não salvar cliente em Interno
            sh.tipo        = 'INTERNO'

        try:
            db.session.commit()
            flash('Stakeholder atualizado!', 'success')
            return redirect(url_for('stakeholders.list'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao atualizar: {e}', 'danger')
    else:
        # Se falhar a validação, mostre os erros (para não ficar "silencioso")
        if request.method == 'POST':
            flash(f'Erros no formulário: {form.errors}', 'danger')

    return render_template('stakeholders/form.html', form=form, title='Editar Stakeholder')




@bp_stakeholders.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    sh = Stakeholder.query.get_or_404(id)
    db.session.delete(sh)
    try:
        db.session.commit()
        flash('Stakeholder removido.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao remover: {e}', 'danger')
    return redirect(url_for('stakeholders.list'))
