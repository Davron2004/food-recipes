import os
import datetime

basedir = os.path.abspath(os.path.dirname(__file__))

ROLE_MANAGER = 'manager'
ROLE_EDITOR = 'editor'

class Config(object):
    @staticmethod
    def get_database_uri() -> str:
        # postgresql+psycopg2 is required for Heroku (and works locally too)
        return (
            os.getenv('DATABASE_URL').replace('postgres://', 'postgresql+psycopg2://', 1)
            if os.getenv('DATABASE_URL')
            else os.getenv("DATABASE_URL", "sqlite://")
        )

    SQLALCHEMY_DATABASE_URI = get_database_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    STATIC_FOLDER = f"{os.getcwd()}/static"
    JWT_ACCESS_TOKEN_EXPIRES = datetime.timedelta(days=2)
