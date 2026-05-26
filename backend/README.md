# Backend — UniTutor

API REST Flask + WebSocket pour la plateforme UniTutor.

## Structure

```
backend/
├── app.py                      # Point d'entrée, SocketIO, blueprints
├── config.py                   # Configuration via variables d'environnement
├── models.py                   # Modèles SQLAlchemy
├── requirements.txt            # Dépendances Python
├── schema.sql                  # Schéma MySQL + données initiales
├── .env.example                # Template de configuration
└── routes/
    ├── auth.py                 # /api/auth
    ├── tuteurs.py              # /api/tuteurs
    ├── sessions_route.py       # /api/sessions
    ├── messagerie.py           # /api/messages
    ├── progression_route.py    # /api/progression
    └── disponibilites.py       # /api/disponibilites
```

## Modèles

| Modèle | Description |
|--------|-------------|
| `Utilisateur` | Étudiant ou tuteur, avec hash de mot de passe |
| `Matiere` | Table de référence des matières (créables par les tuteurs) |
| `Session` | Réservation entre un étudiant et un tuteur |
| `Message` | Messagerie directe entre utilisateurs |
| `Evaluation` | Note 1–5 liée à une session terminée |
| `Progression` | Pourcentage de progression par matière/étudiant |
| `DisponibiliteTuteur` | Créneaux hebdomadaires récurrents d'un tuteur |
| `TuteurMatiereConfig` | Heures par semaine qu'un tuteur consacre à une matière |

## API Endpoints

### Auth — `/api/auth`

| Méthode | URL | Auth | Description |
|---------|-----|------|-------------|
| POST | `/inscription` | — | Créer un compte (connecte automatiquement) |
| POST | `/connexion` | — | Se connecter |
| POST | `/deconnexion` | ✓ | Se déconnecter |
| GET  | `/moi` | ✓ | Profil courant |
| PUT  | `/profil` | ✓ | Modifier son profil |

### Tuteurs — `/api/tuteurs`

| Méthode | URL | Auth | Description |
|---------|-----|------|-------------|
| GET  | `/` | — | Lister les tuteurs (params: `q`, `matiere`) |
| GET  | `/matieres-liste` | — | Toutes les matières disponibles |
| POST | `/matieres-liste` | ✓ tuteur | Créer une nouvelle matière |
| GET  | `/<id>` | — | Détail d'un tuteur |
| PUT  | `/matieres` | ✓ tuteur | Mettre à jour ses matières enseignées |

### Sessions — `/api/sessions`

| Méthode | URL | Auth | Description |
|---------|-----|------|-------------|
| GET  | `/` | ✓ | Mes sessions |
| POST | `/` | ✓ | Créer une session (`tuteur_id`, `date_heure`, `matiere_nom` ou `matiere_id`, `duree_min`, `notes`) |
| PUT  | `/<id>/statut` | ✓ | Changer le statut — si `terminee` par le tuteur, accepte `progression` (0–100) pour mettre à jour la progression de l'étudiant |
| POST | `/<id>/evaluer` | ✓ étudiant | Évaluer une session terminée (note 1–5) |

### Messages — `/api/messages`

| Méthode | URL | Auth | Description |
|---------|-----|------|-------------|
| GET  | `/contacts` | ✓ | Contacts disponibles (tuteurs pour étudiant, étudiants pour tuteur) |
| GET  | `/conversations` | ✓ | Liste des conversations avec dernier message |
| GET  | `/<id>` | ✓ | Historique avec un utilisateur (marque comme lu) |
| POST | `/` | ✓ | Envoyer un message |

### Progression — `/api/progression`

| Méthode | URL | Auth | Description |
|---------|-----|------|-------------|
| GET | `/` | ✓ | Ma progression par matière |
| PUT | `/` | ✓ | Mettre à jour (`matiere_id`, `pourcentage` 0–100) |

### Disponibilités — `/api/disponibilites`

| Méthode | URL | Auth | Description |
|---------|-----|------|-------------|
| GET    | `/` | ✓ tuteur | Mes créneaux hebdomadaires |
| POST   | `/` | ✓ tuteur | Ajouter un créneau (`jour`, `heure_debut`, `heure_fin`) |
| DELETE | `/<id>` | ✓ tuteur | Supprimer un créneau |
| GET    | `/tuteur/<id>` | — | Créneaux d'un tuteur (public) |
| GET    | `/heures` | ✓ tuteur | Mes heures par matière |
| PUT    | `/heures` | ✓ tuteur | Mettre à jour par `matiere_id` |
| PUT    | `/heures-par-nom` | ✓ tuteur | Mettre à jour par `matiere_nom` |
| GET    | `/heures/tuteur/<id>` | — | Heures par matière d'un tuteur (public) |

## WebSocket (SocketIO)

Mode : `threading` (compatible Python 3.13+).

| Événement | Direction | Payload |
|-----------|-----------|---------|
| `rejoindre` | client → serveur | `{ user1, user2 }` |
| `message` | client → serveur | `{ expediteur_id, destinataire_id, contenu }` |
| `nouveau_message` | serveur → room | objet message complet |
| `erreur` | serveur → client | `{ message }` |

## Variables d'environnement

| Variable | Défaut | Description |
|----------|--------|-------------|
| `SECRET_KEY` | `dev-secret-change-in-prod` | Clé de session Flask |
| `MYSQL_HOST` | `localhost` | Hôte MySQL |
| `MYSQL_USER` | `root` | Utilisateur MySQL |
| `MYSQL_PASSWORD` | _(vide)_ | Mot de passe MySQL |
| `MYSQL_DB` | `unitutor` | Nom de la base |

## Pages publiques

| URL | Description |
|-----|-------------|
| `/` | Landing page — présentation de la plateforme |
| `/connexion` | Formulaire de connexion |
| `/inscription` | Formulaire d'inscription |

Les utilisateurs non connectés accédant à une route protégée reçoivent un `401` (API) ou sont redirigés vers `/connexion` (pages HTML).

## Lancer en développement

```bash
cd backend
python app.py
# http://localhost:5000
```

> Testé avec Python 3.13. `eventlet` n'est pas compatible avec Python 3.13+, le mode `threading` est utilisé à la place.
