from flask import Blueprint

learn_bp = Blueprint('learn', __name__, url_prefix='/learn')

from . import routes
