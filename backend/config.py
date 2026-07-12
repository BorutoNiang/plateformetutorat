import os
from dotenv import load_dotenv

load_dotenv()

def _build_db_url():
    # Priorité 1 : MYSQL_URL ou DATABASE_URL (format complet)
    url = os.environ.get('MYSQL_URL') or os.environ.get('DATABASE_URL', '')
    if url:
        if url.startswith('mysql://'):
            url = url.replace('mysql://', 'mysql+mysqlconnector://', 1)
        if '?' not in url:
            url += '?charset=utf8mb4'
        return url

    # Priorité 2 : variables Railway séparées (MYSQLHOST, etc.)
    host = (os.environ.get('MYSQLHOST') or
            os.environ.get('MYSQL_HOST') or 'localhost')
    port = (os.environ.get('MYSQLPORT') or
            os.environ.get('MYSQL_PORT') or '3306')
    user = (os.environ.get('MYSQLUSER') or
            os.environ.get('MYSQL_USER') or 'root')
    pwd  = (os.environ.get('MYSQLPASSWORD') or
            os.environ.get('MYSQL_PASSWORD') or '')
    db   = (os.environ.get('MYSQLDATABASE') or
            os.environ.get('MYSQL_DB') or 'unitutor')

    return (f"mysql+mysqlconnector://{user}:{pwd}"
            f"@{host}:{port}/{db}?charset=utf8mb4")

class Config:
    SECRET_KEY                     = os.environ.get('SECRET_KEY', 'dev-secret-change-in-prod')
    SQLALCHEMY_DATABASE_URI        = _build_db_url()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS      = {
        'connect_args': {'charset': 'utf8mb4'},
        'pool_recycle': 280,
        'pool_pre_ping': True,
    }
