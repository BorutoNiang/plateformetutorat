# Déploiement UniTutor sur Railway

## Prérequis

- Compte [Railway](https://railway.app)
- Compte [GitHub](https://github.com)
- Code pushé sur GitHub (`git push`)

---

## Étape 1 — Créer le projet Railway

1. Va sur [railway.app](https://railway.app) → **New Project**
2. Clique **Deploy from GitHub repo**
3. Autorise Railway à accéder à ton GitHub si demandé
4. Sélectionne le repo `plateformetutorat`
5. Railway détecte le `Procfile` automatiquement

---

## Étape 2 — Ajouter MySQL

1. Dans ton projet Railway, clique **+ New**
2. Sélectionne **Database** → **MySQL**
3. Attends que la base soit provisionnée (30 secondes)
4. Clique sur le service MySQL → onglet **Variables**
5. Copie la valeur de `MYSQL_URL` (format : `mysql://user:password@host:port/dbname`)

---

## Étape 3 — Variables d'environnement

Dans ton service web Railway → onglet **Variables**, ajoute :

| Variable | Valeur |
|----------|--------|
| `SECRET_KEY` | Une chaîne aléatoire longue (ex: `unitutor-prod-secret-2026-xK9mP`) |
| `MYSQL_URL` | La valeur copiée depuis le service MySQL |

---

## Étape 4 — Initialiser la base de données

1. Dans Railway, clique sur le service **MySQL**
2. Onglet **Query** (ou utilise un client MySQL externe avec les credentials Railway)
3. Colle et exécute le contenu de `backend/schema.sql`

Ou depuis ton terminal local avec les credentials Railway :

```bash
mysql -h HOST -P PORT -u USER -pPASSWORD DBNAME < backend/schema.sql
```

Les credentials sont dans l'onglet **Variables** du service MySQL.

---

## Étape 5 — Vérifier le déploiement

1. Onglet **Deployments** → clique sur le déploiement en cours
2. Consulte les **Logs** pour vérifier qu'il n'y a pas d'erreur
3. Clique sur **View** (ou l'URL générée) pour ouvrir le site

L'URL ressemble à : `https://plateformetutorat-production.up.railway.app`

---

## Étape 6 — Déploiements suivants

À chaque modification, pousse sur GitHub et Railway redéploie automatiquement :

```bash
git add .
git commit -m "description des changements"
git push
```

---

## Fichiers de configuration Railway

| Fichier | Rôle |
|---------|------|
| `Procfile` | Commande de démarrage : `gunicorn --worker-class gevent -w 1 app:app` |
| `runtime.txt` | Version Python : `python-3.11.9` |
| `backend/requirements.txt` | Dépendances Python incluant `gunicorn` et `gevent` |
| `backend/config.py` | Lit `MYSQL_URL` ou les variables séparées automatiquement |

---

## Dépannage

**Le déploiement échoue au build**
- Vérifie que `backend/requirements.txt` est bien présent
- Consulte les logs Railway pour l'erreur exacte

**Erreur de connexion à la base**
- Vérifie que `MYSQL_URL` est bien défini dans les variables
- Assure-toi que le service MySQL est bien démarré

**Les pages ne chargent pas**
- Vérifie que `SECRET_KEY` est défini
- Consulte les logs du service web

**WebSocket ne fonctionne pas**
- Railway supporte les WebSockets nativement
- Le mode `gevent` est requis avec gunicorn (déjà configuré dans le `Procfile`)
