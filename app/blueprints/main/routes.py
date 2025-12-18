from flask import Blueprint, render_template
from ...models import Client, Dealer, Equipment, Project

main_bp = Blueprint("main", __name__)

@main_bp.route("/")
def index():
    metrics = {
        'clients': Client.query.count(),
        'dealers': Dealer.query.count(),
        'equipments': Equipment.query.count(),
        'projects': Project.query.count(),
    }
    return render_template("home.html", **metrics)
