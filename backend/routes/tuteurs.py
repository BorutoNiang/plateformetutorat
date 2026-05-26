from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from models import db, Utilisateur, Matiere, tuteur_matieres

tuteurs_bp = Blueprint('tuteurs', __name__, url_prefix='/api/tuteurs')


@tuteurs_bp.route('/', methods=['GET'])
def lister_tuteurs():
    matiere = request.args.get('matiere', '').strip()
    q       = request.args.get('q', '').strip()

    query = Utilisateur.query.filter_by(role='tuteur', actif=True)

    if matiere:
        query = (query
                 .join(tuteur_matieres, Utilisateur.id == tuteur_matieres.c.tuteur_id)
                 .join(Matiere, Matiere.id == tuteur_matieres.c.matiere_id)
                 .filter(Matiere.nom.ilike(f'%{matiere}%')))
    if q:
        query = query.filter(
            db.or_(
                Utilisateur.nom.ilike(f'%{q}%'),
                Utilisateur.prenom.ilike(f'%{q}%'),
                Utilisateur.universite.ilike(f'%{q}%'),
            )
        )

    tuteurs = query.order_by(Utilisateur.note_moy.desc()).all()
    return jsonify([t.to_dict() for t in tuteurs])


@tuteurs_bp.route('/matieres-liste', methods=['GET'])
def liste_matieres():
    """Retourne toutes les matières disponibles."""
    matieres = Matiere.query.order_by(Matiere.nom).all()
    return jsonify([m.to_dict() for m in matieres])


@tuteurs_bp.route('/matieres-liste', methods=['POST'])
@login_required
def creer_matiere():
    """Crée une nouvelle matière (accessible à tous les tuteurs)."""
    if current_user.role != 'tuteur':
        return jsonify({'erreur': 'Accès refusé'}), 403
    data = request.get_json(silent=True) or {}
    nom = data.get('nom', '').strip()
    if not nom:
        return jsonify({'erreur': 'Le nom est requis'}), 400
    if Matiere.query.filter(Matiere.nom.ilike(nom)).first():
        return jsonify({'erreur': 'Cette matière existe déjà'}), 409
    m = Matiere(nom=nom, domaine=data.get('domaine', '').strip() or None)
    db.session.add(m)
    db.session.commit()
    return jsonify(m.to_dict()), 201


@tuteurs_bp.route('/<int:tid>', methods=['GET'])
def detail_tuteur(tid):
    t = Utilisateur.query.filter_by(id=tid, role='tuteur').first_or_404()
    return jsonify(t.to_dict())


@tuteurs_bp.route('/matieres', methods=['PUT'])
@login_required
def maj_matieres():
    if current_user.role != 'tuteur':
        return jsonify({'erreur': 'Accès refusé'}), 403
    data = request.get_json(silent=True) or {}
    ids = data.get('matiere_ids', [])
    current_user.matieres = Matiere.query.filter(Matiere.id.in_(ids)).all()
    db.session.commit()
    return jsonify(current_user.to_dict())
