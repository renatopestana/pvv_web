
# app/blueprints/oc_api/routes.py
from flask import Blueprint, request, jsonify, session, current_app, url_for
from flask_login import login_required
from app.services.operations_center import OperationsCenterClient

bp_oc = Blueprint("oc", __name__, url_prefix="/api/oc")

# Instância da API (vai ser hidratada com tokens do session em cada requisição)
oc_client = OperationsCenterClient()


@bp_oc.get("/machines")
@login_required
def machines():
    org_id = (request.args.get("org_id") or "").strip()
    if not org_id:
        return jsonify({"error": "org_id is required"}), 400

    # Hidrata tokens do session nesta instância antes de chamar a API
    access = session.get("oc_access_token")
    refresh = session.get("oc_refresh_token")

    if not access:
        # Ainda não autenticado no Operations Center → forçar 2ª etapa (Okta/Deere)
        return jsonify({"error": "not_authorized"}), 401

    oc_client.access_token = access
    oc_client.refresh_token = refresh

    try:
        items = oc_client.get_machines_by_org(org_id)
        return jsonify({"values": items}), 200

    except RuntimeError as e:
        # Tipicamente token ausente/expirado/refresh falhou
        return jsonify({"error": "not_authorized", "detail": str(e)}), 401

    except Exception as e:
        # Erros de rede/OC API → log e 502
        current_app.logger.exception("Erro ao consultar máquinas (org_id=%s)", org_id)
        return jsonify({"error": "oc_api_error", "detail": str(e)}), 502
