from flask import Blueprint

walkthrough_bp = Blueprint('walkthrough', __name__, url_prefix='/walkthrough')

from . import routes
