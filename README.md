# UniTutor — Plateforme de tutorat universitaire

Plateforme web qui connecte étudiants et tuteurs universitaires pour des sessions de tutorat personnalisées, avec messagerie temps réel, suivi de progression et gestion des disponibilités.

**Stack :** Python / Flask · MySQL · HTML / CSS / JS vanilla · SocketIO

**Démo en ligne :** https://web-production-6b78b.up.railway.app

---

## Structure du projet

```
unitutor/
├── backend/                        # API Flask
│   ├── app.py                      # Point d'entrée, SocketIO, blueprints
│   ├── config.py                   # Configuration (DB, secret key)
│   ├── models.py                   # Modèles SQLAlchemy
│   ├── requirements.txt            # Dépendances Python
│   ├── schema.sql                  # Schéma MySQL local
│   ├── schema_railway.sql          # Schéma MySQL pour Railway (sans CREATE DATABASE)
│   ├── .env.example                # Template variables d'environnement
│   └── routes/
│       ├── auth.py                 # /api/auth
│       ├── tuteurs.py              # /api/tuteurs
│       ├── sessions_route.py       # /api/sessions
│       ├── messagerie.py           # /api/messages
│       ├── progression_route.py    # /api/progression
│       └── disponibilites.py       # /api/disponibilites
├── frontend/                       # Interface utilisateur
│   ├── templates/                  # Pages Jinja2
│   └── static/                     # CSS + JS
├── Procfile                        # Commande de démarrage Railway (gunicorn)
├── nixpacks.toml                   # Config build Railway
├── runtime.txt                     # Version Python (3.11.9)
├── requirements.txt                # Dépendances (copie racine pour Railway)
├── DEPLOY.md                       # Guide de déploiement Railway
└── README.md                       # Ce fichier
```

---

## Fonctionnalités

### Étudiant
- Recherche et filtrage de tuteurs par nom, université ou matière
- Consultation des créneaux hebdomadaires et heures/matière des tuteurs
- Demande de session avec choix de la matière, date, durée et message
- Messagerie temps réel avec les tuteurs
- Suivi de progression par matière (mis à jour par le tuteur)
- Historique des sessions passées
- Évaluation des sessions (note 1–5)

### Tuteur
- Tableau de bord avec statistiques (sessions, heures, note moyenne)
- Gestion des demandes de sessions (confirmer / annuler)
- Marquer une session comme terminée + noter la progression de l'étudiant
- Gestion des matières enseignées (sélection + création de nouvelles matières)
- Définition des créneaux hebdomadaires et heures par matière
- Messagerie temps réel avec les étudiants

### Général
- Page de présentation publique (landing page)
- Inscription / connexion avec redirection automatique selon le rôle
- Chat WebSocket temps réel (Socket.IO)

---

## Installation locale

### 1. Cloner et installer les dépendances

```bash
git clone https://github.com/BorutoNiang/plateformetutorat.git
cd plateformetutorat
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r backend/requirements.txt
```

### 2. Créer la base de données MySQL

```cmd
mysql -u root -p --default-character-set=utf8mb4 < backend/schema.sql
```

### 3. Configurer les variables d'environnement

```bash
copy backend\.env.example backend\.env
```

Remplis `backend/.env` :

```
SECRET_KEY=une-cle-secrete-longue
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=ton_mot_de_passe
MYSQL_DB=unitutor
```

### 4. Lancer

```bash
cd backend
python app.py
```

Accès : http://localhost:5000

---

## Déploiement Railway

Voir [DEPLOY.md](DEPLOY.md) pour le guide complet.

### Résumé rapide

1. Créer un projet Railway depuis ce repo GitHub
2. Ajouter un service MySQL dans Railway
3. Initialiser la base :
```cmd
mysql -h HOST -P PORT -u root -pPASSWORD railway --default-character-set=utf8mb4 < backend/schema_railway.sql
```
4. Ajouter les variables d'environnement dans le service web :
   - `SECRET_KEY` — clé secrète
   - `MYSQL_URL` — URL MySQL interne Railway

---

## API — Endpoints principaux

| Méthode | URL | Description |
|---------|-----|-------------|
| POST | `/api/auth/inscription` | Créer un compte |
| POST | `/api/auth/connexion` | Se connecter |
| GET  | `/api/auth/moi` | Profil courant |
| GET  | `/api/tuteurs/` | Lister tuteurs (params: `q`, `matiere`) |
| GET  | `/api/tuteurs/matieres-liste` | Toutes les matières |
| POST | `/api/tuteurs/matieres-liste` | Créer une matière (tuteur) |
| GET  | `/api/sessions/` | Mes sessions |
| POST | `/api/sessions/` | Créer une session |
| PUT  | `/api/sessions/:id/statut` | Changer statut + progression |
| GET  | `/api/messages/contacts` | Contacts disponibles |
| GET  | `/api/messages/conversations` | Mes conversations |
| POST | `/api/messages/` | Envoyer un message |
| GET  | `/api/progression/` | Ma progression |
| GET  | `/api/disponibilites/` | Mes créneaux |
| POST | `/api/disponibilites/` | Ajouter un créneau |

---

## WebSocket

| Événement | Description |
|-----------|-------------|
| `rejoindre` | Rejoindre une room de conversation |
| `message` | Envoyer un message temps réel |
| `nouveau_message` | Recevoir un message |

---

## Pages

| URL | Description |
|-----|-------------|
| `/` | Landing page publique |
| `/connexion` | Connexion |
| `/inscription` | Inscription |
| `/tableau-de-bord` | Dashboard étudiant |
| `/matching` | Recherche de tuteurs |
| `/messagerie` | Chat temps réel |
| `/suivi` | Progression & historique |
| `/tuteur/dashboard` | Dashboard tuteur |
| `/tuteur/sessions` | Gestion des sessions |
| `/tuteur/matieres` | Gestion des matières |
| `/tuteur/disponibilites` | Créneaux & heures/matière |
