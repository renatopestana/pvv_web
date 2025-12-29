# app/__init__.py
from flask import Flask
from .extensions import db, migrate, login_manager, csrf
from app.utils.oc_callback_bridge import start_oc_callback_bridge


def create_app(config_object="config.DevConfig"):
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config.from_object(config_object)

    # Inicializa extensões
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)

    # Importa models dentro do contexto da app (Alembic autogenerate enxerga tudo)
    with app.app_context():
        from . import models  # noqa: F401
        from .models import User  # para o user_loader

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    login_manager.login_view = "auth.login"
    login_manager.login_message = "Por favor, faça login para acessar a página."

    # Importa e registra blueprints APÓS inicializar extensões e carregar models

    from .blueprints.clients import clients_bp
    from .blueprints.dealers import dealers_bp
    from .blueprints.projects import projects_bp
    from .blueprints.statuses import statuses_bp
    from .blueprints.inventory import inventory_bp
    from .blueprints.main import main_bp
    from .blueprints.functional_areas import bp_functional_areas
    from .blueprints.positions import bp_positions
    from .blueprints.stakeholders import bp_stakeholders
    from .blueprints.activities.routes import bp_activities
    from .blueprints.oc_api.routes import bp_oc
    from app.blueprints.auth.routes import auth_local_bp
    from app.blueprints.auth_oidc.routes import bp_auth_oidc

    app.register_blueprint(clients_bp, url_prefix="/clientes")
    app.register_blueprint(dealers_bp, url_prefix="/concessionarios")
    app.register_blueprint(projects_bp, url_prefix="/projetos")
    app.register_blueprint(statuses_bp, url_prefix="/statuses")
    app.register_blueprint(inventory_bp, url_prefix="/equipamentos")
    app.register_blueprint(bp_functional_areas, url_prefix="/areas_funcionais")
    app.register_blueprint(bp_positions, url_prefix="/cargos")
    app.register_blueprint(bp_stakeholders, url_prefix="/stakeholders")
    app.register_blueprint(main_bp, url_prefix="/")
    app.register_blueprint(bp_activities)
    app.register_blueprint(bp_oc)
    app.register_blueprint(auth_local_bp)
    app.register_blueprint(bp_auth_oidc)

    try:
        start_oc_callback_bridge(host="127.0.0.1", port=9090)
    except Exception as e:
        app.logger.warning(f"OC bridge not started: {e}")
    return app

