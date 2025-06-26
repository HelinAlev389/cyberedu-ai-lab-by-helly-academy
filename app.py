import os
from flask import Flask, redirect, url_for
from config import Config
from extensions import db, migrate, login_manager, mail
from flask_wtf import CSRFProtect
from models.user import User
from blueprints import register_blueprints

csrf = CSRFProtect()


def create_app():
    app = Flask(__name__, static_folder="static")
    app.config.from_object(Config)

    basedir = os.path.abspath(os.path.dirname(__file__))
    db_path = os.getenv('DATABASE_PATH', os.path.join(basedir, 'data', 'app.db'))
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{db_path}"
    app.config['SQLALCHEMY_ECHO'] = app.config.get("DEBUG", False)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    mail.init_app(app)
    csrf.init_app(app)

    login_manager.login_view = 'auth.login'

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    # Регистриране на всички blueprints
    register_blueprints(app)

    @app.route('/')
    def home_redirect():
        return redirect(url_for('auth.login'))


    return app


# ─── Стартиране ───
if __name__ == "__main__":
    flask_app = create_app()

    with flask_app.app_context():
        print("DB URI:", flask_app.config['SQLALCHEMY_DATABASE_URI'])
        if flask_app.config['SQLALCHEMY_DATABASE_URI'].startswith("sqlite:///"):
            db.create_all()

    flask_app.run(debug=flask_app.config.get("DEBUG", False))
