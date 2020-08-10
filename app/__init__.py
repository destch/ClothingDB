from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_bootstrap import Bootstrap
from flask_migrate import Migrate
from flask_login import LoginManager
from config import config
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

db = SQLAlchemy()
bootstrap = Bootstrap()
login_manager = LoginManager()

login_manager.login_view = "auth.login"

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    db.init_app(app)
    bootstrap.init_app(app)
    migrate = Migrate(app, db)
    login_manager.init_app(app)
    if config_name == "production":
        sentry_sdk.init(dsn="https://d8b30011e1ee4cc4bf8be7540065b334@o419385.ingest.sentry.io/5331956", integrations=[FlaskIntegration()])

    from .main import main as main_blueprint

    app.register_blueprint(main_blueprint, url_prefix="/")

    from .API import api as api_blueprint

    app.register_blueprint(api_blueprint, url_prefix="/api")

    from .auth import auth as auth_blueprint

    app.register_blueprint(auth_blueprint, url_prefix="/auth")

    return app
