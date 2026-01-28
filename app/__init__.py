from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
import os

db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()

def create_app():
    template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates'))
    static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'static'))

    app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
    app.config.from_object('config.Config')

    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    login_manager.login_view = 'auth.login'

    with app.app_context():
        from app.models import User

        @login_manager.user_loader
        def load_user(user_id):
            return User.query.get(int(user_id))

    # Import des blueprints
    from app.auth import auth
    from app.main import main
    from app.employees import employees
    from app.recruitment import recruitment_bp
    from app.termination import termination_bp
    from app.prediction_routes import prediction_bp

    # Enregistrement des blueprints
    app.register_blueprint(auth)
    app.register_blueprint(main)
    app.register_blueprint(employees)
    app.register_blueprint(recruitment_bp)
    app.register_blueprint(termination_bp)
    app.register_blueprint(prediction_bp)

    # Invoke-RestMethod -Uri "http://localhost:5000/prediction/predict" -Method POST -ContentType "application/json" -Body '{"start_year": 2025, "end_year": 2027, "recruitments": 100, "departures": 50, "initial_employees": 1000}'Exemption CSRF pour le blueprint de prédiction
    csrf.exempt(prediction_bp)

    return app