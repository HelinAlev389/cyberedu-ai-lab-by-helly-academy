from flask import Flask, redirect, url_for
from config import Config
from extensions import db, migrate, login_manager, mail
from blueprints import register_blueprints
import os

def create_app():
    app = Flask(__name__, static_folder="static")
    app.config.from_object(Config)

    # ——— set up absolute path for SQLite DB ———
    basedir = os.path.abspath(os.path.dirname(__file__))
    db_path = os.path.join(basedir, 'data', 'app.db')
    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    # note: three slashes + absolute path gives 'sqlite:///C:/...'
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{db_path}"
    # optional but helpful: echo SQL to console
    app.config['SQLALCHEMY_ECHO'] = True
    # ————————————————————————————————————————

    # initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    mail.init_app(app)
    login_manager.login_view = 'auth.login'

    # flask-login user loader
    from models.user import User
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # register blueprints
    register_blueprints(app)

    @app.route('/')
    def home_redirect():
        return redirect(url_for('auth.login'))

    return app


if __name__ == "__main__":
    app = create_app()

    # push context before creating tables
    with app.app_context():
        # debug output to verify the exact file path
        print("DB URI:", app.config['SQLALCHEMY_DATABASE_URI'])
        db.create_all()

    app.run(debug=True)
