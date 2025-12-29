
# app/blueprints/auth_oidc/routes.py
from flask import Blueprint, redirect, request, url_for, session
from flask_login import login_required
from app.services.operations_center import OperationsCenterClient

bp_auth_oidc = Blueprint("auth_oidc", __name__, url_prefix="/auth")
oc_client = OperationsCenterClient()

@bp_auth_oidc.get("/login")
@login_required
def login():
    session["post_login_next"] = request.args.get("next") or url_for("main.index")
    return redirect(oc_client.authorization_url())

@bp_auth_oidc.get("/callback")
def callback():
    code = request.args.get("code")
    state = request.args.get("state")
    oc_client.exchange_code(code)

    # guarda tokens (serão usados pela oc_api)
    session["oc_access_token"]  = oc_client.access_token
    session["oc_refresh_token"] = oc_client.refresh_token

    next_url = session.pop("post_login_next", url_for("main.index"))
    return redirect(next_url)
