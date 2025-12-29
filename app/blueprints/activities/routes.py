# app/blueprints/activities/routes.py
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from sqlalchemy.orm import selectinload
from datetime import datetime
from app.extensions import db
from app.forms import projects
from app.forms import activities
from app.models import Activity, Project, User, Client, Dealer, Equipment, Status
from app.forms.activities import ActivityForm

bp_activities = Blueprint('activities', __name__, url_prefix='/atividades')

def _fill_choices(form: ActivityForm):
    form.project_id.choices = [(p.id, p.name) for p in db.session.query(Project).order_by(Project.name.asc()).all()]
    form.owner_user_id.choices = [(u.id, u.full_name) for u in db.session.query(User).order_by(User.full_name.asc()).all()]
    form.executor_user_id.choices = [(u.id, u.full_name) for u in db.session.query(User).order_by(User.full_name.asc()).all()]
    form.client_id.choices = [(0, '— Selecione —')] + [(c.id, c.name) for c in db.session.query(Client).order_by(Client.nome_razao.asc()).all()]
    form.dealer_id.choices = [(0, '— Selecione —')] + [(d.id, d.razao_social) for d in db.session.query(Dealer).order_by(Dealer.razao_social.asc()).all()]
    form.equipment_ids.choices = [(e.id, e.name) for e in db.session.query(Equipment).order_by(Equipment.name.asc()).all()]
    form.status_id.choices = [(s.id, s.nome) for s in db.session.query(Status).order_by(Status.nome.asc()).all()]


@bp_activities.route('/')
@login_required
def list():
    q = (request.args.get('q') or '').strip()
    project_id = request.args.get('project_id', type=int)
    status_id = request.args.get('status_id', type=int)
    environment = (request.args.get('environment') or '').strip().upper()
    owner_id    = request.args.get('owner_id', type=int)
    executor_id = request.args.get('executor_id', type=int)

    query = db.session.query(Activity).options(
        selectinload(Activity.project),
        selectinload(Activity.owner_user),
        selectinload(Activity.executor_user),
        selectinload(Activity.client),
        selectinload(Activity.dealer),
        selectinload(Activity.status),
        selectinload(Activity.equipments),
    )

    if q:
        query = query.filter(Activity.description.ilike(f'%{q}%'))
    if project_id:
        query = query.filter(Activity.project_id == project_id)
    if status_id:
        query = query.filter(Activity.status_id == status_id)
    if environment in ('SIMULADO', 'CONTROLADO', 'REAL'):
        query = query.filter(Activity.environment == environment)
    if owner_id:
        query = query.filter(Activity.owner_user_id == owner_id)
    if executor_id:
        query = query.filter(Activity.executor_user_id == executor_id)


    activities = query.order_by(Activity.start_date.desc(), Activity.created_at.desc()).all()

    # filtros (dropdowns)
    projects = db.session.query(Project).order_by(Project.name.asc()).all()
    statuses = db.session.query(Status).order_by(Status.nome.asc()).all()
    owners    = db.session.query(User).order_by(User.full_name.asc()).all()
    executors = owners  # mesma lista de usuário

    return render_template(
        'activities/list.html',
        activities=activities,
        q=q, project_id=project_id, status_id=status_id, environment=environment,
        owner_id=owner_id, executor_id=executor_id,
        projects=projects, statuses=statuses, owners=owners, executors=executors
    )


@bp_activities.route('/new', methods=['GET', 'POST'])
@login_required
def create():
    form = ActivityForm()
    _fill_choices(form)

    # normaliza placeholders
    if request.method == 'POST':
        if form.client_id.data == 0:
            form.client_id.data = None
        if form.dealer_id.data == 0:
            form.dealer_id.data = None

    if form.validate_on_submit():
        # calcula duração se não informada e houver end_date
        duration = form.duration_hours.data
        if duration is None and form.end_date.data:
            delta = (form.end_date.data - form.start_date.data).days
            if delta is not None and delta >= 0:
                duration = float(delta * 24)

        activity = Activity(
            description=form.description.data.strip(),
            project_id=form.project_id.data,
            start_date=form.start_date.data,
            end_date=form.end_date.data,
            duration_hours=duration,
            owner_user_id=form.owner_user_id.data,
            executor_user_id=form.executor_user_id.data,
            environment=form.environment.data,
            client_id=form.client_id.data,
            dealer_id=form.dealer_id.data,
            machines_text=",".join(form.machine_serials.data or []),
            status_id=form.status_id.data,
        )

        # equipamentos (M2M)
        if form.equipment_ids.data:
            eqs = db.session.query(Equipment).filter(Equipment.id.in_(form.equipment_ids.data)).all()
            activity.equipments = eqs

        db.session.add(activity)
        try:
            db.session.commit()
            flash('Atividade criada com sucesso!', 'success')
            return redirect(url_for('activities.list'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao salvar: {e}', 'danger')

    return render_template('activities/form.html', form=form, title='Nova Atividade')

@bp_activities.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    activity = db.session.query(Activity).get_or_404(id)
    form = ActivityForm(obj=activity)
    _fill_choices(form)

    # Preenche multiselect com ids de equipamentos
    form.equipment_ids.data = [e.id for e in activity.equipments] if request.method == 'GET' else form.equipment_ids.data

    if request.method == 'POST':
        if form.client_id.data == 0:
            form.client_id.data = None
        if form.dealer_id.data == 0:
            form.dealer_id.data = None

    if form.validate_on_submit():
        activity.description = form.description.data.strip()
        activity.project_id = form.project_id.data
        activity.start_date = form.start_date.data
        activity.end_date = form.end_date.data
        activity.duration_hours = form.duration_hours.data
        activity.owner_user_id = form.owner_user_id.data
        activity.executor_user_id = form.executor_user_id.data
        activity.environment = form.environment.data
        activity.client_id = form.client_id.data
        activity.dealer_id = form.dealer_id.data
        activity.machines_text = ",".join(form.machine_serials.data or [])
        activity.status_id = form.status_id.data

        # equipamentos
        eqs = db.session.query(Equipment).filter(Equipment.id.in_(form.equipment_ids.data or [])).all()
        activity.equipments = eqs

        try:
            db.session.commit()
            flash('Atividade atualizada!', 'success')
            return redirect(url_for('activities.list'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao atualizar: {e}', 'danger')

    return render_template('activities/form.html', form=form, title='Editar Atividade')

@bp_activities.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    activity = db.session.query(Activity).get_or_404(id)
    db.session.delete(activity)
    try:
        db.session.commit()
        flash('Atividade removida.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao remover: {e}', 'danger')
    return redirect(url_for('activities.list'))
