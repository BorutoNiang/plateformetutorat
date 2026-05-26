from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from models import db, DisponibiliteTuteur, TuteurMatiereConfig, Matiere, Utilisateur

dispo_bp = Blueprint('disponibilites', __name__, url_prefix='/api/disponibilites')

JOURS_VALIDES = ('lundi', 'mardi', 'mercredi', 'jeudi', 'vendredi', 'samedi', 'dimanche')


# ── Disponibilités (créneaux) ────────────────────────────────

@dispo_bp.route('/', methods=['GET'])
@login_required
def mes_disponibilites():
    dispos = DisponibiliteTuteur.query.filter_by(tuteur_id=current_user.id).order_by(
        DisponibiliteTuteur.jour, DisponibiliteTuteur.heure_debut
    ).all()
    return jsonify([d.to_dict() for d in dispos])


@dispo_bp.route('/tuteur/<int:tid>', methods=['GET'])
def disponibilites_tuteur(tid):
    """Public — pour afficher les créneaux d'un tuteur dans le matching."""
    dispos = DisponibiliteTuteur.query.filter_by(tuteur_id=tid).order_by(
        DisponibiliteTuteur.jour, DisponibiliteTuteur.heure_debut
    ).all()
    return jsonify([d.to_dict() for d in dispos])


@dispo_bp.route('/', methods=['POST'])
@login_required
def ajouter_disponibilite():
    if current_user.role != 'tuteur':
        return jsonify({'erreur': 'Accès refusé'}), 403
    data = request.get_json(silent=True) or {}

    jour        = data.get('jour', '').lower()
    heure_debut = data.get('heure_debut', '')
    heure_fin   = data.get('heure_fin', '')

    if jour not in JOURS_VALIDES:
        return jsonify({'erreur': f'Jour invalide. Valeurs : {", ".join(JOURS_VALIDES)}'}), 400
    if not heure_debut or not heure_fin:
        return jsonify({'erreur': 'heure_debut et heure_fin sont requis (format HH:MM)'}), 400
    if heure_debut >= heure_fin:
        return jsonify({'erreur': 'heure_fin doit être après heure_debut'}), 400

    d = DisponibiliteTuteur(
        tuteur_id=current_user.id,
        jour=jour,
        heure_debut=heure_debut,
        heure_fin=heure_fin,
    )
    db.session.add(d)
    db.session.commit()
    return jsonify(d.to_dict()), 201


@dispo_bp.route('/<int:did>', methods=['DELETE'])
@login_required
def supprimer_disponibilite(did):
    d = DisponibiliteTuteur.query.get_or_404(did)
    if d.tuteur_id != current_user.id:
        return jsonify({'erreur': 'Accès refusé'}), 403
    db.session.delete(d)
    db.session.commit()
    return jsonify({'message': 'Supprimé'}), 200


# ── Heures par matière ───────────────────────────────────────

@dispo_bp.route('/heures', methods=['GET'])
@login_required
def mes_heures():
    configs = TuteurMatiereConfig.query.filter_by(tuteur_id=current_user.id).all()
    return jsonify([c.to_dict() for c in configs])


@dispo_bp.route('/heures/tuteur/<int:tid>', methods=['GET'])
def heures_tuteur(tid):
    """Public — heures par matière d'un tuteur."""
    configs = TuteurMatiereConfig.query.filter_by(tuteur_id=tid).all()
    return jsonify([c.to_dict() for c in configs])


@dispo_bp.route('/heures', methods=['PUT'])
@login_required
def maj_heures():
    """Met à jour les heures/semaine pour une ou plusieurs matières."""
    if current_user.role != 'tuteur':
        return jsonify({'erreur': 'Accès refusé'}), 403
    data = request.get_json(silent=True) or {}
    items = data if isinstance(data, list) else [data]

    for item in items:
        mid   = item.get('matiere_id')
        heures = int(item.get('heures_par_semaine', 1))
        if not mid or heures < 1 or heures > 40:
            continue
        cfg = TuteurMatiereConfig.query.filter_by(
            tuteur_id=current_user.id, matiere_id=mid
        ).first()
        if not cfg:
            cfg = TuteurMatiereConfig(tuteur_id=current_user.id, matiere_id=mid)
            db.session.add(cfg)
        cfg.heures_par_semaine = heures

    db.session.commit()
    return jsonify([c.to_dict() for c in TuteurMatiereConfig.query.filter_by(tuteur_id=current_user.id).all()])


@dispo_bp.route('/heures-par-nom', methods=['PUT'])
@login_required
def maj_heures_par_nom():
    """Reçoit [{ matiere_nom, heures_par_semaine }] et résout les IDs."""
    if current_user.role != 'tuteur':
        return jsonify({'erreur': 'Accès refusé'}), 403
    items = request.get_json(silent=True) or []
    for item in items:
        nom    = item.get('matiere_nom', '').strip()
        heures = int(item.get('heures_par_semaine', 1))
        if not nom or heures < 1 or heures > 40:
            continue
        mat = Matiere.query.filter(Matiere.nom.ilike(nom)).first()
        if not mat:
            continue
        cfg = TuteurMatiereConfig.query.filter_by(
            tuteur_id=current_user.id, matiere_id=mat.id
        ).first()
        if not cfg:
            cfg = TuteurMatiereConfig(tuteur_id=current_user.id, matiere_id=mat.id)
            db.session.add(cfg)
        cfg.heures_par_semaine = heures
    db.session.commit()
    return jsonify([c.to_dict() for c in TuteurMatiereConfig.query.filter_by(tuteur_id=current_user.id).all()])
