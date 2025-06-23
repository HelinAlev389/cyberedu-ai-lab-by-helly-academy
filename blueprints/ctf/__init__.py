from flask import Blueprint

ctf_bp = Blueprint('ctf', __name__, url_prefix='/ctf')

from . import routes
