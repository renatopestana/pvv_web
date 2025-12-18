from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required
from app.extensions import db
from app.forms.functional_areas import FunctionalAreaDeleteForm
from app.models import FunctionalArea
from app.forms import FunctionalAreaForm
from . import bp_functional_areas   


@bp_functional_areas.route('/')
@login_required
def list():
    q = request.args.get('q', '').strip()
    query = FunctionalArea.query
    if q:
        query = query.filter(FunctionalArea.name.ilike(f'%{q}%'))
    areas = query.order_by(FunctionalArea.name.asc()).all()
    delete_forms = {a.id: FunctionalAreaDeleteForm() for a in areas}
    return render_template('functional_areas/list.html', areas=areas, q=q, delete_forms=delete_forms)


@bp_functional_areas.route('/new', methods=['GET', 'POST'])
@login_required
def create():
    form = FunctionalAreaForm()
    if form.validate_on_submit():
        area = FunctionalArea(name=form.name.data.strip())
        db.session.add(area)
        try:
            db.session.commit()
            flash('Área funcional criada com sucesso!', 'success')
            return redirect(url_for('functional_areas.list'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao salvar: {e}', 'danger')
    return render_template('functional_areas/form.html', form=form, title='Nova Área Funcional')


@bp_functional_areas.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    area = FunctionalArea.query.get_or_404(id)
    form = FunctionalAreaForm(obj=area)
    if form.validate_on_submit():
        area.name = form.name.data.strip()
        try:
            db.session.commit()
            flash('Área funcional atualizada!', 'success')
            return redirect(url_for('functional_areas.list'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao atualizar: {e}', 'danger')
    return render_template('functional_areas/form.html', form=form, title='Editar Área Funcional')


@bp_functional_areas.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    area = FunctionalArea.query.get_or_404(id)
    form = FunctionalAreaDeleteForm()
    if form.validate_on_submit():
        try:
            db.session.delete(area)
            db.session.commit()
            flash('Área funcional removida.', 'success')
            return redirect(url_for('functional_areas.list'))
        except Exception as e:
            flash(f'Erro ao remover: {e}', 'danger')
            db.session.rollback()
    return redirect(url_for('functional_areas.list'))
