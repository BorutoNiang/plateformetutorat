from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime
from sqlalchemy import func
from models import db, Session, Utilisateur, Matiere, Evaluation, Progression

sessions_bp = Blueprint('sessions', __name__, url_prefix='/api/sessions')


@sessions_bp.route('/', methods=['GET'])
@login_required
def mes_sessions():
    if current_user.role == 'etudiant':
        sess = Session.query.filter_by(etudiant_id=current_user.id).order_by(Session.date_heure).all()
    else:
        sess = Session.query.filter_by(tuteur_id=current_user.id).order_by(Session.date_heure).all()
    return jsonify([s.to_dict() for s in sess])


@sessions_bp.route('/', methods=['POST'])
@login_required
def creer_session():
    data = request.get_json(silent=True) or {}

    if not data.get('tuteur_id') or not data.get('date_heure'):
        return jsonify({'erreur': 'tuteur_id et date_heure sont requis'}), 400

    # Résolution de la matière : accepte matiere_id (int) ou matiere_nom (str)
    matiere_id = data.get('matiere_id')
    if not matiere_id and data.get('matiere_nom'):
        mat = Matiere.query.filter_by(nom=data['matiere_nom']).first()
        matiere_id = mat.id if mat else None

    try:
        date_heure = datetime.fromisoformat(data['date_heure'])
    except ValueError:
        return jsonify({'erreur': 'Format de date invalide (ISO 8601 attendu)'}), 400

    tuteur = Utilisateur.query.filter_by(id=data['tuteur_id'], role='tuteur').first()
    if not tuteur:
        return jsonify({'erreur': 'Tuteur introuvable'}), 404

    s = Session(
        etudiant_id=current_user.id,
        tuteur_id=data['tuteur_id'],
        matiere_id=matiere_id,
        date_heure=date_heure,
        duree_min=int(data.get('duree_min', 60)),
        notes=data.get('notes', '').strip() or None,
    )
    db.session.add(s)
    tuteur.nb_sessions += 1
    db.session.commit()
    return jsonify(s.to_dict()), 201


@sessions_bp.route('/<int:sid>/statut', methods=['PUT'])
@login_required
def maj_statut(sid):
    s = Session.query.get_or_404(sid)
    if current_user.id not in (s.tuteur_id, s.etudiant_id):
        return jsonify({'erreur': 'Accès refusé'}), 403

    data = request.get_json(silent=True) or {}
    statuts_valides = ('en_attente', 'confirmee', 'terminee', 'annulee')
    if data.get('statut') not in statuts_valides:
        return jsonify({'erreur': 'Statut invalide'}), 400

    s.statut = data['statut']

    # Si le tuteur marque la session comme terminée et fournit une progression
    if data['statut'] == 'terminee' and current_user.id == s.tuteur_id:
        pourcentage = data.get('progression')
        if pourcentage is not None and s.matiere_id:
            pourcentage = max(0, min(100, int(pourcentage)))
            p = Progression.query.filter_by(
                etudiant_id=s.etudiant_id,
                matiere_id=s.matiere_id,
            ).first()
            if not p:
                p = Progression(etudiant_id=s.etudiant_id, matiere_id=s.matiere_id)
                db.session.add(p)
            p.pourcentage = pourcentage

    db.session.commit()
    return jsonify(s.to_dict())


@sessions_bp.route('/<int:sid>/evaluer', methods=['POST'])
@login_required
def evaluer(sid):
    s = Session.query.get_or_404(sid)

    if s.statut != 'terminee':
        return jsonify({'erreur': 'La session doit être terminée pour être évaluée'}), 403
    if s.etudiant_id != current_user.id:
        return jsonify({'erreur': 'Seul l\'étudiant peut évaluer la session'}), 403
    if s.evaluation:
        return jsonify({'erreur': 'Session déjà évaluée'}), 409

    data = request.get_json(silent=True) or {}
    note = data.get('note')
    if not isinstance(note, int) or not (1 <= note <= 5):
        return jsonify({'erreur': 'La note doit être un entier entre 1 et 5'}), 400

    e = Evaluation(
        session_id=sid,
        auteur_id=current_user.id,
        note=note,
        commentaire=data.get('commentaire', ''),
    )
    db.session.add(e)
    db.session.flush()  # persiste l'évaluation avant le calcul

    # Recalcul correct de la note moyenne du tuteur
    tuteur = Utilisateur.query.get(s.tuteur_id)
    result = (db.session.query(func.avg(Evaluation.note))
              .join(Session, Session.id == Evaluation.session_id)
              .filter(Session.tuteur_id == tuteur.id)
              .scalar())
    tuteur.note_moy = round(float(result), 2) if result else 0

    db.session.commit()
    return jsonify({'message': 'Évaluation enregistrée'}), 201
