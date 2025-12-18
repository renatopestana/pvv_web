from flask import Blueprint
bp_positions = Blueprint('positions', __name__, url_prefix='/positions')
from . import routes  # noqa
