from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required
from app.extensions import db
from app.models import Stakeholder, Client, Position
from app.forms import StakeholderForm
from . import bp_stakeholders

# app/blueprints/stakeholders/routes.py
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
    q = request.args.get('q', '').strip()
    tipo = request.args.get('tipo', '').strip().upper()
    query = Stakeholder.query
    if q:
        query = query.filter(Stakeholder.name.ilike(f'%{q}%'))
    if tipo in ('INTERNO', 'EXTERNO'):
        query = query.filter(Stakeholder.tipo == tipo)
    stakeholders = query.order_by(Stakeholder.created_at.desc()).all()
    return render_template('stakeholders/list.html', stakeholders=stakeholders, q=q, tipo=tipo)

@bp_stakeholders.route('/new', methods=['GET', 'POST'])
@login_required
def create():
    form = StakeholderForm()
    _fill_choices(form)
    if request.method == 'POST':
        # Converte "0" para None para passar na validação
        if form.client_id.data == 0:
            form.client_id.data = None
        if form.position_id.data == 0:
            form.position_id.data = None

    if form.validate_on_submit():
        sh = Stakeholder(
            name=form.name.data.strip(),
            tipo=form.tipo.data,
            client_id=form.client_id.data if form.tipo.data == 'EXTERNO' else None,
            position_id=form.position_id.data if form.tipo.data == 'INTERNO' else None
        )
        db.session.add(sh)
        try:
            db.session.commit()
            flash('Stakeholder criado com sucesso!', 'success')
            return redirect(url_for('stakeholders.list'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao salvar: {e}', 'danger')
    return render_template('stakeholders/form.html', form=form, title='Novo Stakeholder')

@bp_stakeholders.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    sh = Stakeholder.query.get_or_404(id)
    form = StakeholderForm(obj=sh)
    _fill_choices(form)
    if request.method == 'POST':
        if form.client_id.data == 0:
            form.client_id.data = None
        if form.position_id.data == 0:
            form.position_id.data = None

    if form.validate_on_submit():
        sh.name = form.name.data.strip()
        sh.tipo = form.tipo.data
        sh.client_id = form.client_id.data if form.tipo.data == 'EXTERNO' else None
        sh.position_id = form.position_id.data if form.tipo.data == 'INTERNO' else None
        try:
            db.session.commit()
            flash('Stakeholder atualizado!', 'success')
            return redirect(url_for('stakeholders.list'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao atualizar: {e}', 'danger')
    else:
        # Ajusta SelectField com 0 quando None (para renderização)
        if sh.client_id is None:
            form.client_id.data = 0
        if sh.position_id is None:
            form.position_id.data = 0

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
