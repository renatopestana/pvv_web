from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required
from app.extensions import db
from app.models import Position, FunctionalArea
from app.forms import PositionForm
from . import bp_positions

def _fill_area_choices(form):
    form.functional_area_id.choices = [(a.id, a.name) for a in FunctionalArea.query.order_by(FunctionalArea.name.asc()).all()]

@bp_positions.route('/')
@login_required
def list():
    q = request.args.get('q', '').strip()
    area_id = request.args.get('area_id', type=int)
    query = Position.query
    if q:
        query = query.filter(Position.name.ilike(f'%{q}%'))
    if area_id:
        query = query.filter(Position.functional_area_id == area_id)
    positions = query.order_by(Position.name.asc()).all()
    areas = FunctionalArea.query.order_by(FunctionalArea.name.asc()).all()
    return render_template('positions/list.html', positions=positions, areas=areas, q=q, area_id=area_id)

@bp_positions.route('/new', methods=['GET', 'POST'])
@login_required
def create():
    form = PositionForm()
    _fill_area_choices(form)
    if form.validate_on_submit():
        pos = Position(
            name=form.name.data.strip(),
            functional_area_id=form.functional_area_id.data
        )
        db.session.add(pos)
        try:
            db.session.commit()
            flash('Posição criada com sucesso!', 'success')
            return redirect(url_for('positions.list'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao salvar: {e}', 'danger')
    return render_template('positions/form.html', form=form, title='Nova Posição')

@bp_positions.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    pos = Position.query.get_or_404(id)
    form = PositionForm(obj=pos)
    _fill_area_choices(form)
    if form.validate_on_submit():
        pos.name = form.name.data.strip()
        pos.functional_area_id = form.functional_area_id.data
        try:
            db.session.commit()
            flash('Posição atualizada!', 'success')
            return redirect(url_for('positions.list'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao atualizar: {e}', 'danger')
    return render_template('positions/form.html', form=form, title='Editar Posição')

@bp_positions.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    pos = Position.query.get_or_404(id)
    db.session.delete(pos)
    try:
        db.session.commit()
        flash('Posição removida.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao remover: {e}', 'danger')
    return redirect(url_for('positions.list'))
