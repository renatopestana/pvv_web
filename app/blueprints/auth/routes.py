from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from ...extensions import db
from ...models import User
from ...forms.auth import RegisterForm, LoginForm

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    form = RegisterForm()
    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data.lower()).first():
            flash("E-mail já cadastrado.", "error")
        else:
            user = User(full_name=form.full_name.data.strip(),
                        email=form.email.data.lower().strip(),
                        cpf=(form.cpf.data or "").strip())
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            flash("Conta criada com sucesso. Faça login.", "success")
            return redirect(url_for("auth.login"))
    return render_template("auth/register.html", form=form)

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            flash("Bem-vindo!", "success")
            next_page = request.args.get("next") or url_for("main.index")
            return redirect(next_page)
        flash("Credenciais Inválidas.", "error")
    return render_template("auth/login.html", form=form)

@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Sessão encerrada.", "info")
    return redirect(url_for("auth.login"))


@auth_bp.route("/reset_password", methods=["GET", "POST"])
def reset_password():
    # Aqui você pode implementar a lógica de redefinição de senha
    return render_template("auth/reset_password.html")
