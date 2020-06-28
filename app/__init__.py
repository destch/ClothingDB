from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_bootstrap import Bootstrap
from flask_migrate import Migrate
from flask_login import LoginManager

db = SQLAlchemy()
bootstrap = Bootstrap()
login_manager = LoginManager()
login_manager.login_view = "auth.login"
admin = Admin(name='app', template_mode='bootstrap3')


def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')
    app.debug = True
    db.init_app(app)
    admin.init_app(app)
    bootstrap.init_app(app)
    migrate = Migrate(app, db)
    login_manager.init_app(app)

    from .admin import bp as admin_bp
    app.register_blueprint(admin_bp, url_prefix='/admin')

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint, url_prefix='/')

    from .API import api as api_blueprint
    app.register_blueprint(api_blueprint, url_prefix='/api')

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    return app