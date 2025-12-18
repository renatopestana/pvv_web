# app/blueprints/projects/routes.py
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from ...extensions import db
from ...models import Project, Status  # NOVO: importar Status
from ...forms.projects import ProjectForm, DeleteProjectForm

projects_bp = Blueprint("projects", __name__)  # assumindo url_prefix no register_blueprint

# Helper: filtra status marcados para "Projetos" e retorna choices [(id, nome), ...]
def _project_status_choices():
    PROJECT_TAGS = ("projeto", "projetos")  # termos aceitos (case-insensitive)
    statuses = Status.query.order_by(Status.nome.asc()).all()

    def is_for_projects(s):
        # Trata 'tipos_cadastro' como lista/array OU string, e 'tipo_cadastro' (singular) como string
        candidates = []
        if hasattr(s, "tipos_cadastro") and s.tipos_cadastro:
            if isinstance(s.tipos_cadastro, (list, tuple, set)):
                candidates = [str(x).strip().lower() for x in s.tipos_cadastro]
            else:
                candidates = [str(s.tipos_cadastro).lower()]
        elif hasattr(s, "tipo_cadastro") and s.tipo_cadastro:
            candidates = [str(s.tipo_cadastro).lower()]
        # Critério: contém algum dos termos "projeto"/"projetos"
        return any(any(tag in c for tag in PROJECT_TAGS) for c in candidates)

    filtered = [s for s in statuses if is_for_projects(s)]
    # 0 = opção neutra ("Selecione..."); manter coerção para int no form
    return [(0, "— Selecione —")] + [(s.id, s.nome) for s in filtered]


@projects_bp.route("/", methods=["GET"])
@login_required
def list_():
    q = request.args.get("q", "").strip()
    query = Project.query
    if q:
        query = query.filter(Project.name.ilike(f"%{q}%"))
    projects = query.order_by(Project.name.asc()).all()
    delete_forms = {p.id: DeleteProjectForm() for p in projects}
    return render_template("projects/list.html", projects=projects, delete_forms=delete_forms)


@projects_bp.route("/novo", methods=["GET", "POST"])
@login_required
def create():
    form = ProjectForm()
    # Preencher choices SEMPRE antes de validar/renderizar
    form.status_id.choices = _project_status_choices()

    if form.validate_on_submit():
        name = (form.name.data or "").strip()
        if not name:
            flash("O nome do projeto é obrigatório.", "warning")
            return render_template("projects/form.html", form=form, mode="create")

        # Duplicidade por nome
        if Project.query.filter(Project.name.ilike(name)).first():
            flash("Já existe um projeto com esse nome.", "warning")
            return render_template("projects/form.html", form=form, mode="create")

        status_value = form.status_id.data or 0
        status_id = None if status_value == 0 else status_value

        p = Project(
            name=name,
            description=form.description.data,
            status_id=status_id,   # NOVO
        )
        db.session.add(p)
        db.session.commit()
        flash("Projeto salvo.", "success")
        return redirect(url_for("projects.list_"))

    return render_template("projects/form.html", form=form, mode="create")


@projects_bp.route("/<int:project_id>/editar", methods=["GET", "POST"])
@login_required
def edit(project_id):
    p = Project.query.get_or_404(project_id)
    form = ProjectForm(obj=p)
    # Preencher choices ANTES de validar
    form.status_id.choices = _project_status_choices()

    # Ajustar seleção atual na tela (GET): se None, usar 0
    if request.method == "GET":
        form.status_id.data = p.status_id or 0

    if form.validate_on_submit():
        name = (form.name.data or "").strip()
        if not name:
            flash("O nome do projeto é obrigatório.", "warning")
            return render_template("projects/form.html", form=form, mode="edit", project=p)

        dup = Project.query.filter(Project.id != p.id, Project.name.ilike(name)).first()
        if dup:
            flash("Já existe outro projeto com esse nome.", "warning")
            return render_template("projects/form.html", form=form, mode="edit", project=p)

        status_value = form.status_id.data or 0
        p.name = name
        p.description = form.description.data
        p.status_id = None if status_value == 0 else status_value  # NOVO

        db.session.commit()
        flash("Projeto atualizado.", "success")
        return redirect(url_for("projects.list_"))

    return render_template("projects/form.html", form=form, mode="edit", project=p)


@projects_bp.route("/<int:project_id>/excluir", methods=["POST"])
@login_required
def delete(project_id):
    p = Project.query.get_or_404(project_id)
    form = DeleteProjectForm()
    if form.validate_on_submit():
        try:
            db.session.delete(p)
            db.session.commit()
            flash("Projeto excluído com sucesso.", "success")
        except Exception as e:
            db.session.rollback()
            flash("Não foi possível excluir o projeto. Tente novamente.", "danger")
    else:
        flash("Não foi possível excluir o projeto (falha de validação).", "danger")
    return redirect(url_for("projects.list_"))