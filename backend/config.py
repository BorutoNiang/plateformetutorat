import os
import sys

try:
    from dotenv import load_dotenv
    load_dotenv(override=False)
except ImportError:
    pass

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-change-in-prod')

    # Essaie toutes les variables possibles dans l'ordre de priorité
    _db = (os.environ.get('DATABASE_URL') or
           os.environ.get('MYSQL_PUBLIC_URL') or
           os.environ.get('MYSQL_URL') or '')

    if _db:
        if _db.startswith('mysql://'):
            _db = _db.replace('mysql://', 'mysql+mysqlconnector://', 1)
        if '?' not in _db:
            _db += '?charset=utf8mb4'
    else:
        _h  = os.environ.get('MYSQLHOST', 'localhost')
        _p  = os.environ.get('MYSQLPORT', '3306')
        _u  = os.environ.get('MYSQLUSER', 'root')
        _pw = os.environ.get('MYSQLPASSWORD', '')
        _d  = os.environ.get('MYSQLDATABASE', 'unitutor')
        _db = f"mysql+mysqlconnector://{_u}:{_pw}@{_h}:{_p}/{_d}?charset=utf8mb4"

    print(f"[CONFIG] DB: {'REMOTE' if 'localhost' not in _db else 'localhost'} | {_db[:50]}", file=sys.stderr)

    SQLALCHEMY_DATABASE_URI        = _db
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS      = {
        'connect_args': {'charset': 'utf8mb4'},
        'pool_recycle': 280,
        'pool_pre_ping': True,
    }
