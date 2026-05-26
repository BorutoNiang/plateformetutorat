from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from models import db, Message, Utilisateur, Session as Sess
from sqlalchemy import or_, and_, func

msg_bp = Blueprint('messages', __name__, url_prefix='/api/messages')


@msg_bp.route('/contacts', methods=['GET'])
@login_required
def contacts():
    """
    Contacts disponibles pour démarrer une conversation :
    - Étudiant → tous les tuteurs actifs
    - Tuteur   → tous les étudiants ayant une session avec lui
    """
    uid = current_user.id
    if current_user.role == 'etudiant':
        users = (Utilisateur.query
                 .filter_by(role='tuteur', actif=True)
                 .order_by(Utilisateur.nom).all())
    else:
        sous = (db.session.query(Sess.etudiant_id)
                .filter_by(tuteur_id=uid)
                .distinct().subquery())
        users = (Utilisateur.query
                 .filter(Utilisateur.id.in_(sous))
                 .order_by(Utilisateur.nom).all())
    return jsonify([u.to_dict() for u in users])


@msg_bp.route('/conversations', methods=['GET'])
@login_required
def conversations():
    uid = current_user.id

    sous_query = (
        db.session.query(
            func.greatest(Message.expediteur_id, Message.destinataire_id).label('u_max'),
            func.least(Message.expediteur_id, Message.destinataire_id).label('u_min'),
            func.max(Message.id).label('last_id'),
        )
        .filter(or_(Message.expediteur_id == uid, Message.destinataire_id == uid))
        .group_by('u_max', 'u_min')
        .subquery()
    )

    convs = []
    for row in db.session.execute(db.select(sous_query)).all():
        dernier  = db.session.get(Message, row.last_id)
        autre_id = row.u_max if row.u_min == uid else row.u_min
        autre    = db.session.get(Utilisateur, autre_id)
        if not autre or not dernier:
            continue
        non_lus = Message.query.filter_by(
            expediteur_id=autre_id, destinataire_id=uid, lu=False
        ).count()
        convs.append({
            'utilisateur':     autre.to_dict(),
            'dernier_message': dernier.to_dict(),
            'non_lus':         non_lus,
        })

    convs.sort(key=lambda c: c['dernier_message']['envoye_le'], reverse=True)
    return jsonify(convs)


@msg_bp.route('/<int:autre_id>', methods=['GET'])
@login_required
def historique(autre_id):
    uid = current_user.id
    msgs = (
        Message.query
        .filter(or_(
            and_(Message.expediteur_id == uid,      Message.destinataire_id == autre_id),
            and_(Message.expediteur_id == autre_id, Message.destinataire_id == uid),
        ))
        .order_by(Message.envoye_le)
        .all()
    )
    Message.query.filter_by(
        expediteur_id=autre_id, destinataire_id=uid, lu=False
    ).update({'lu': True})
    db.session.commit()
    return jsonify([m.to_dict() for m in msgs])


@msg_bp.route('/', methods=['POST'])
@login_required
def envoyer():
    data = request.get_json(silent=True) or {}
    if not data.get('destinataire_id') or not data.get('contenu', '').strip():
        return jsonify({'erreur': 'destinataire_id et contenu sont requis'}), 400

    dest = db.session.get(Utilisateur, data['destinataire_id'])
    if not dest:
        return jsonify({'erreur': 'Destinataire introuvable'}), 404

    m = Message(
        expediteur_id=current_user.id,
        destinataire_id=data['destinataire_id'],
        contenu=data['contenu'].strip(),
    )
    db.session.add(m)
    db.session.commit()
    return jsonify(m.to_dict()), 201
