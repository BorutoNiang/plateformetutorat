import os
from dotenv import load_dotenv

load_dotenv()

def _build_db_url():
    url = os.environ.get('MYSQL_URL') or os.environ.get('DATABASE_URL', '')
    if url:
        if url.startswith('mysql://'):
            url = url.replace('mysql://', 'mysql+mysqlconnector://', 1)
        if '?' not in url:
            url += '?charset=utf8mb4'
        return url
    host = os.environ.get('MYSQL_HOST', 'localhost')
    user = os.environ.get('MYSQL_USER', 'root')
    pwd  = os.environ.get('MYSQL_PASSWORD', '')
    db   = os.environ.get('MYSQL_DB', 'unitutor')
    return f"mysql+mysqlconnector://{user}:{pwd}@{host}/{db}?charset=utf8mb4"

class Config:
    SECRET_KEY                  = os.environ.get('SECRET_KEY', 'dev-secret-change-in-prod')
    SQLALCHEMY_DATABASE_URI     = _build_db_url()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS   = {
        'connect_args': {'charset': 'utf8mb4'},
        'pool_recycle': 280,
        'pool_pre_ping': True,
    }
