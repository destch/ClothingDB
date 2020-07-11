import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    DEBUG = True
    WTF_CSRF_ENABLED = True
    SECRET_KEY = "secret"
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(basedir, "ClothingDB.sqlite")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    FLASKY_ADMIN = "daniel.chavez9797@gmail.com"
    PROPOGATE_EXCEPTIONS = True

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DEV_DATABASE_URL"
    ) or "sqlite:///" + os.path.join(basedir, "ClothingDB.sqlite")


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get("TEST_DATABASE_URL") or "sqlite://"
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL"
    ) or "sqlite:///" + os.path.join(basedir, "ClothingDB.sqlite")


config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
