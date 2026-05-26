from flask import Blueprint, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from models import db, Utilisateur

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


@auth_bp.route('/inscription', methods=['POST'])
def inscription():
    data = request.get_json(silent=True) or {}
    required = ('nom', 'prenom', 'email', 'mot_de_passe')
    if not all(data.get(k) for k in required):
        return jsonify({'erreur': 'Champs obligatoires manquants'}), 400

    if Utilisateur.query.filter_by(email=data['email'].lower()).first():
        return jsonify({'erreur': 'Email déjà utilisé'}), 409

    u = Utilisateur(
        nom=data['nom'].strip(),
        prenom=data['prenom'].strip(),
        email=data['email'].lower().strip(),
        role=data.get('role', 'etudiant'),
        universite=data.get('universite', '').strip() or None,
        niveau=data.get('niveau', '').strip() or None,
    )
    u.set_password(data['mot_de_passe'])
    db.session.add(u)
    db.session.commit()
    login_user(u)
    return jsonify({'message': 'Compte créé', 'utilisateur': u.to_dict()}), 201


@auth_bp.route('/connexion', methods=['POST'])
def connexion():
    data = request.get_json(silent=True) or {}
    if not data.get('email') or not data.get('mot_de_passe'):
        return jsonify({'erreur': 'Email et mot de passe requis'}), 400

    u = Utilisateur.query.filter_by(email=data['email'].lower().strip()).first()
    if not u or not u.check_password(data['mot_de_passe']):
        return jsonify({'erreur': 'Identifiants incorrects'}), 401

    if not u.actif:
        return jsonify({'erreur': 'Compte désactivé'}), 403

    login_user(u, remember=data.get('souvenir', False))
    return jsonify({'message': 'Connecté', 'utilisateur': u.to_dict()})


@auth_bp.route('/deconnexion', methods=['POST'])
@login_required
def deconnexion():
    logout_user()
    return jsonify({'message': 'Déconnecté'})


@auth_bp.route('/moi', methods=['GET'])
@login_required
def moi():
    return jsonify(current_user.to_dict())


@auth_bp.route('/profil', methods=['PUT'])
@login_required
def modifier_profil():
    data = request.get_json(silent=True) or {}
    for champ in ('nom', 'prenom', 'universite', 'niveau', 'bio'):
        if champ in data:
            setattr(current_user, champ, data[champ])
    db.session.commit()
    return jsonify(current_user.to_dict())
