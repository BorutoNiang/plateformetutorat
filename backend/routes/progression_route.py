from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from models import db, Progression, Matiere

prog_bp = Blueprint('progression', __name__, url_prefix='/api/progression')


@prog_bp.route('/', methods=['GET'])
@login_required
def ma_progression():
    progs = Progression.query.filter_by(etudiant_id=current_user.id).all()
    return jsonify([p.to_dict() for p in progs])


@prog_bp.route('/', methods=['PUT'])
@login_required
def maj_progression():
    data = request.get_json(silent=True) or {}

    if not data.get('matiere_id'):
        return jsonify({'erreur': 'matiere_id est requis'}), 400

    pourcentage = data.get('pourcentage', 0)
    if not isinstance(pourcentage, int) or not (0 <= pourcentage <= 100):
        return jsonify({'erreur': 'pourcentage doit être un entier entre 0 et 100'}), 400

    matiere = db.session.get(Matiere, data['matiere_id'])
    if not matiere:
        return jsonify({'erreur': 'Matière introuvable'}), 404

    p = Progression.query.filter_by(
        etudiant_id=current_user.id,
        matiere_id=data['matiere_id'],
    ).first()

    if not p:
        p = Progression(etudiant_id=current_user.id, matiere_id=data['matiere_id'])
        db.session.add(p)

    p.pourcentage = pourcentage
    db.session.commit()
    return jsonify(p.to_dict())
