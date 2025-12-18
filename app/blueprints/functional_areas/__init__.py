from flask import Blueprint

bp_functional_areas = Blueprint('functional_areas', __name__, url_prefix='/functional-areas')

from . import routes  # noqa
