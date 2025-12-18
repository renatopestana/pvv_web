from flask import Blueprint
bp_stakeholders = Blueprint('stakeholders', __name__, url_prefix='/stakeholders')
from . import routes  # noqa
