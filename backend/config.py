import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-change-in-prod')

    # Railway fournit MYSQL_URL ou DATABASE_URL au format :
    # mysql://user:password@host:port/dbname
    # On le préfère si disponible, sinon on reconstruit depuis les variables séparées.
    _db_url = os.environ.get('MYSQL_URL') or os.environ.get('DATABASE_URL', '')

    if _db_url:
        # Railway utilise parfois "mysql://" — SQLAlchemy veut "mysql+mysqlconnector://"
        if _db_url.startswith('mysql://'):
            _db_url = _db_url.replace('mysql://', 'mysql+mysqlconnector://', 1)
        SQLALCHEMY_DATABASE_URI = _db_url + '?charset=utf8mb4'
    else:
        MYSQL_HOST     = os.environ.get('MYSQL_HOST',     'localhost')
        MYSQL_USER     = os.environ.get('MYSQL_USER',     'root')
        MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', '')
        MYSQL_DB       = os.environ.get('MYSQL_DB',       'unitutor')
        SQLALCHEMY_DATABASE_URI = (
            f"mysql+mysqlconnector://{MYSQL_USER}:{MYSQL_PASSWORD}"
            f"@{MYSQL_HOST}/{MYSQL_DB}?charset=utf8mb4&collation=utf8mb4_unicode_ci"
        )

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'connect_args': {'charset': 'utf8mb4'},
        'pool_recycle': 280,   # évite les connexions mortes sur Railway
        'pool_pre_ping': True,
    }
