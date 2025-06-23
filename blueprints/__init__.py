# blueprints/__init__.py

from .auth.routes import auth_bp
from .dashboard.routes import dashboard_bp
from .ctf.routes import ctf_bp
from .siem.routes import siem_bp
from .profile.routes import profile_bp
from .walkthrough.routes import walkthrough_bp
from .learn.routes import learn_bp


def register_blueprints(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(ctf_bp)
    app.register_blueprint(siem_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(walkthrough_bp)
    app.register_blueprint(learn_bp)
