from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

# ── Association tuteur <-> matières ─────────────────────────
tuteur_matieres = db.Table(
    'tuteur_matieres',
    db.Column('tuteur_id',  db.Integer, db.ForeignKey('utilisateurs.id'), primary_key=True),
    db.Column('matiere_id', db.Integer, db.ForeignKey('matieres.id'),     primary_key=True)
)


class Utilisateur(UserMixin, db.Model):
    __tablename__ = 'utilisateurs'

    id           = db.Column(db.Integer, primary_key=True)
    nom          = db.Column(db.String(100), nullable=False)
    prenom       = db.Column(db.String(100), nullable=False)
    email        = db.Column(db.String(255), unique=True, nullable=False)
    mot_de_passe = db.Column(db.String(255), nullable=False)
    role         = db.Column(db.Enum('etudiant', 'tuteur'), default='etudiant')
    universite   = db.Column(db.String(200))
    niveau       = db.Column(db.String(100))
    bio          = db.Column(db.Text)
    photo        = db.Column(db.String(255))
    note_moy     = db.Column(db.Numeric(3, 2), default=0)
    nb_sessions  = db.Column(db.Integer, default=0)
    actif        = db.Column(db.Boolean, default=True)
    cree_le      = db.Column(db.DateTime, default=datetime.utcnow)

    matieres          = db.relationship('Matiere', secondary=tuteur_matieres, backref='tuteurs')
    sessions_etudiant = db.relationship('Session', foreign_keys='Session.etudiant_id', backref='etudiant')
    sessions_tuteur   = db.relationship('Session', foreign_keys='Session.tuteur_id',   backref='tuteur')
    messages_envoyes  = db.relationship('Message', foreign_keys='Message.expediteur_id',   backref='expediteur')
    messages_recus    = db.relationship('Message', foreign_keys='Message.destinataire_id',  backref='destinataire')

    def set_password(self, password: str) -> None:
        self.mot_de_passe = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.mot_de_passe, password)

    @property
    def nom_complet(self) -> str:
        return f"{self.prenom} {self.nom}"

    @property
    def initiales(self) -> str:
        return f"{self.prenom[0]}{self.nom[0]}".upper()

    def to_dict(self) -> dict:
        return {
            'id':         self.id,
            'nom':        self.nom,
            'prenom':     self.prenom,
            'email':      self.email,
            'role':       self.role,
            'universite': self.universite,
            'niveau':     self.niveau,
            'bio':        self.bio,
            'note_moy':   float(self.note_moy or 0),
            'nb_sessions': self.nb_sessions,
            'matieres':   [m.nom for m in self.matieres],
        }


class Matiere(db.Model):
    __tablename__ = 'matieres'

    id      = db.Column(db.Integer, primary_key=True)
    nom     = db.Column(db.String(150), unique=True, nullable=False)
    domaine = db.Column(db.String(100))

    def to_dict(self) -> dict:
        return {'id': self.id, 'nom': self.nom, 'domaine': self.domaine}


class Session(db.Model):
    __tablename__ = 'sessions'

    id          = db.Column(db.Integer, primary_key=True)
    etudiant_id = db.Column(db.Integer, db.ForeignKey('utilisateurs.id'), nullable=False)
    tuteur_id   = db.Column(db.Integer, db.ForeignKey('utilisateurs.id'), nullable=False)
    matiere_id  = db.Column(db.Integer, db.ForeignKey('matieres.id'))
    date_heure  = db.Column(db.DateTime, nullable=False)
    duree_min   = db.Column(db.Integer, default=60)
    statut      = db.Column(
        db.Enum('en_attente', 'confirmee', 'terminee', 'annulee'),
        default='en_attente'
    )
    notes   = db.Column(db.Text)
    cree_le = db.Column(db.DateTime, default=datetime.utcnow)

    matiere    = db.relationship('Matiere')
    evaluation = db.relationship('Evaluation', uselist=False, backref='session')

    def to_dict(self) -> dict:
        return {
            'id':         self.id,
            'etudiant':   self.etudiant.nom_complet if self.etudiant else None,
            'tuteur':     self.tuteur.nom_complet   if self.tuteur   else None,
            'matiere':    self.matiere.nom           if self.matiere  else None,
            'matiere_id': self.matiere_id,
            'date_heure': self.date_heure.isoformat(),
            'duree_min':  self.duree_min,
            'statut':     self.statut,
            'notes':      self.notes,
        }


class Message(db.Model):
    __tablename__ = 'messages'

    id              = db.Column(db.Integer, primary_key=True)
    expediteur_id   = db.Column(db.Integer, db.ForeignKey('utilisateurs.id'), nullable=False)
    destinataire_id = db.Column(db.Integer, db.ForeignKey('utilisateurs.id'), nullable=False)
    contenu         = db.Column(db.Text, nullable=False)
    lu              = db.Column(db.Boolean, default=False)
    envoye_le       = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self) -> dict:
        return {
            'id':               self.id,
            'expediteur_id':    self.expediteur_id,
            'destinataire_id':  self.destinataire_id,
            'contenu':          self.contenu,
            'lu':               self.lu,
            'envoye_le':        self.envoye_le.isoformat(),
        }


class Evaluation(db.Model):
    __tablename__ = 'evaluations'

    id          = db.Column(db.Integer, primary_key=True)
    session_id  = db.Column(db.Integer, db.ForeignKey('sessions.id'), unique=True)
    auteur_id   = db.Column(db.Integer, db.ForeignKey('utilisateurs.id'))
    note        = db.Column(db.SmallInteger, nullable=False)
    commentaire = db.Column(db.Text)
    cree_le     = db.Column(db.DateTime, default=datetime.utcnow)


class Progression(db.Model):
    __tablename__ = 'progression'

    id          = db.Column(db.Integer, primary_key=True)
    etudiant_id = db.Column(db.Integer, db.ForeignKey('utilisateurs.id'))
    matiere_id  = db.Column(db.Integer, db.ForeignKey('matieres.id'))
    pourcentage = db.Column(db.SmallInteger, default=0)
    maj_le      = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    matiere  = db.relationship('Matiere')
    etudiant = db.relationship('Utilisateur')

    def to_dict(self) -> dict:
        return {
            'matiere':     self.matiere.nom if self.matiere else None,
            'matiere_id':  self.matiere_id,
            'pourcentage': self.pourcentage,
        }


class DisponibiliteTuteur(db.Model):
    """Créneaux hebdomadaires récurrents d'un tuteur."""
    __tablename__ = 'disponibilites'

    id         = db.Column(db.Integer, primary_key=True)
    tuteur_id  = db.Column(db.Integer, db.ForeignKey('utilisateurs.id'), nullable=False)
    jour       = db.Column(db.Enum('lundi','mardi','mercredi','jeudi','vendredi','samedi','dimanche'), nullable=False)
    heure_debut = db.Column(db.String(5), nullable=False)   # "08:00"
    heure_fin   = db.Column(db.String(5), nullable=False)   # "10:00"
    cree_le    = db.Column(db.DateTime, default=datetime.utcnow)

    tuteur = db.relationship('Utilisateur', backref='disponibilites')

    def to_dict(self) -> dict:
        return {
            'id':          self.id,
            'jour':        self.jour,
            'heure_debut': self.heure_debut,
            'heure_fin':   self.heure_fin,
        }


class TuteurMatiereConfig(db.Model):
    """Heures hebdomadaires qu'un tuteur consacre à une matière."""
    __tablename__ = 'tuteur_matiere_config'

    id                  = db.Column(db.Integer, primary_key=True)
    tuteur_id           = db.Column(db.Integer, db.ForeignKey('utilisateurs.id'), nullable=False)
    matiere_id          = db.Column(db.Integer, db.ForeignKey('matieres.id'), nullable=False)
    heures_par_semaine  = db.Column(db.SmallInteger, default=1)
    __table_args__      = (db.UniqueConstraint('tuteur_id', 'matiere_id'),)

    tuteur  = db.relationship('Utilisateur', backref='matiere_configs')
    matiere = db.relationship('Matiere')

    def to_dict(self) -> dict:
        return {
            'matiere_id':         self.matiere_id,
            'matiere_nom':        self.matiere.nom if self.matiere else None,
            'heures_par_semaine': self.heures_par_semaine,
        }
