from flask import Blueprint

siem_bp = Blueprint('siem', __name__, url_prefix='/siem')

from . import routes
