import os
from flask import Flask, render_template
from flask_login import LoginManager
from flask_socketio import SocketIO, emit, join_room
from config import Config
from models import db, Utilisateur, Message

# ── App factory ──────────────────────────────────────────────
app = Flask(
    __name__,
    template_folder=os.path.join('..', 'frontend', 'templates'),
    static_folder=os.path.join('..', 'frontend', 'static'),
)
app.config.from_object(Config)

db.init_app(app)

# Override DB URL depuis les variables d'environnement runtime
# (nécessaire quand config est chargé avant que Railway injecte les vars)
import os as _os
_runtime_url = (_os.environ.get('DATABASE_URL') or
                _os.environ.get('MYSQL_URL') or '')
if _runtime_url:
    if _runtime_url.startswith('mysql://'):
        _runtime_url = _runtime_url.replace('mysql://', 'mysql+mysqlconnector://', 1)
    if '?' not in _runtime_url:
        _runtime_url += '?charset=utf8mb4'
    app.config['SQLALCHEMY_DATABASE_URI'] = _runtime_url
    print(f"[DB] Runtime override: {_runtime_url[:50]}", file=__import__('sys').stderr)
else:
    _h = _os.environ.get('MYSQLHOST') or _os.environ.get('MYSQL_HOST') or ''
    if _h:
        _p = _os.environ.get('MYSQLPORT') or '3306'
        _u = _os.environ.get('MYSQLUSER') or 'root'
        _pw = _os.environ.get('MYSQLPASSWORD') or ''
        _db = _os.environ.get('MYSQLDATABASE') or 'railway'
        _runtime_url = f"mysql+mysqlconnector://{_u}:{_pw}@{_h}:{_p}/{_db}?charset=utf8mb4"
        app.config['SQLALCHEMY_DATABASE_URI'] = _runtime_url
        print(f"[DB] Runtime from vars: host={_h} db={_db}", file=__import__('sys').stderr)

# Force utf8mb4 sur chaque connexion
from sqlalchemy import event, text
from sqlalchemy.engine import Engine

@event.listens_for(Engine, "connect")
def set_unicode(dbapi_conn, connection_record):
    cursor = dbapi_conn.cursor()
    cursor.execute("SET NAMES utf8mb4 COLLATE utf8mb4_unicode_ci")
    cursor.close()
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# ── Auth ─────────────────────────────────────────────────────
login_manager = LoginManager(app)
login_manager.login_view = 'connexion_page'

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(Utilisateur, int(user_id))

@login_manager.unauthorized_handler
def unauthorized():
    from flask import request, jsonify
    if request.path.startswith('/api/'):
        return jsonify({'erreur': 'Non authentifié'}), 401
    return render_template('connexion.html'), 401

# ── Blueprints ───────────────────────────────────────────────
from routes.auth             import auth_bp
from routes.tuteurs          import tuteurs_bp
from routes.sessions_route   import sessions_bp
from routes.messagerie       import msg_bp
from routes.progression_route import prog_bp
from routes.disponibilites   import dispo_bp

app.register_blueprint(auth_bp)
app.register_blueprint(tuteurs_bp)
app.register_blueprint(sessions_bp)
app.register_blueprint(msg_bp)
app.register_blueprint(prog_bp)
app.register_blueprint(dispo_bp)

# ── Pages HTML ───────────────────────────────────────────────
@app.route('/')
def index():
    return render_template('landing.html')

@app.route('/connexion')
def connexion_page():
    return render_template('connexion.html')

@app.route('/inscription')
def inscription_page():
    return render_template('inscription.html')

@app.route('/tableau-de-bord')
def dashboard():
    return render_template('dashboard.html')

@app.route('/matching')
def matching():
    return render_template('matching.html')

@app.route('/messagerie')
def messagerie():
    return render_template('messagerie.html')

@app.route('/suivi')
def suivi():
    return render_template('suivi.html')

# ── Pages tuteur ─────────────────────────────────────────────
@app.route('/tuteur/dashboard')
def tuteur_dashboard():
    return render_template('tuteur_dashboard.html')

@app.route('/tuteur/sessions')
def tuteur_sessions():
    return render_template('tuteur_sessions.html')

@app.route('/tuteur/matieres')
def tuteur_matieres():
    return render_template('tuteur_matieres.html')

@app.route('/tuteur/disponibilites')
def tuteur_disponibilites():
    return render_template('tuteur_disponibilites.html')

# ── WebSocket : chat temps réel ──────────────────────────────
@socketio.on('rejoindre')
def on_join(data):
    u1, u2 = int(data['user1']), int(data['user2'])
    room = f"conv_{min(u1, u2)}_{max(u1, u2)}"
    join_room(room)

@socketio.on('message')
def handle_message(data):
    try:
        m = Message(
            expediteur_id=int(data['expediteur_id']),
            destinataire_id=int(data['destinataire_id']),
            contenu=data['contenu'].strip(),
        )
        db.session.add(m)
        db.session.commit()
        u1, u2 = m.expediteur_id, m.destinataire_id
        room = f"conv_{min(u1, u2)}_{max(u1, u2)}"
        emit('nouveau_message', m.to_dict(), room=room)
    except Exception as e:
        emit('erreur', {'message': str(e)})

# ── Entrée ───────────────────────────────────────────────────
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, debug=True, host='0.0.0.0', port=port)
