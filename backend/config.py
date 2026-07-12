import os
import sys

# Ne pas utiliser load_dotenv en production - Railway injecte les vars directement
try:
    from dotenv import load_dotenv
    load_dotenv(override=False)  # Ne pas écraser les vars déjà définies
except ImportError:
    pass

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-change-in-prod')

    # Lire DATABASE_URL directement - Railway l'injecte au runtime
    _db = os.environ.get('DATABASE_URL', '')
    if not _db:
        _h  = os.environ.get('MYSQLHOST', 'localhost')
        _p  = os.environ.get('MYSQLPORT', '3306')
        _u  = os.environ.get('MYSQLUSER', 'root')
        _pw = os.environ.get('MYSQLPASSWORD', '')
        _d  = os.environ.get('MYSQLDATABASE', 'unitutor')
        _db = f"mysql+mysqlconnector://{_u}:{_pw}@{_h}:{_p}/{_d}?charset=utf8mb4"
    elif _db.startswith('mysql://'):
        _db = _db.replace('mysql://', 'mysql+mysqlconnector://', 1)
    elif _db.startswith('mysql+mysqlconnector://') and '?' not in _db:
        _db += '?charset=utf8mb4'

    print(f"[CONFIG] DB host check: {'localhost' if 'localhost' in _db else 'REMOTE'}", file=sys.stderr)

    SQLALCHEMY_DATABASE_URI        = _db
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS      = {
        'connect_args': {'charset': 'utf8mb4'},
        'pool_recycle': 280,
        'pool_pre_ping': True,
    }
