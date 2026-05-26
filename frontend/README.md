# Frontend — UniTutor

Interface utilisateur de la plateforme UniTutor. HTML / CSS / JS vanilla servi par Flask via Jinja2.

## Structure

```
frontend/
├── templates/
│   ├── base.html                  # Layout minimal (fonts, CSS, JS)
│   ├── app_base.html              # Layout avec sidebar + topbar (pages connectées)
│   ├── landing.html               # Page de présentation publique
│   ├── connexion.html             # Page de connexion
│   ├── inscription.html           # Page d'inscription
│   ├── dashboard.html             # Tableau de bord étudiant
│   ├── matching.html              # Recherche de tuteurs
│   ├── messagerie.html            # Chat temps réel
│   ├── suivi.html                 # Progression & historique des sessions
│   ├── tuteur_dashboard.html      # Tableau de bord tuteur
│   ├── tuteur_sessions.html       # Gestion des sessions (tuteur)
│   ├── tuteur_matieres.html       # Gestion des matières enseignées
│   └── tuteur_disponibilites.html # Créneaux hebdomadaires & heures/matière
└── static/
    ├── css/style.css              # Thème sombre, tous les composants
    └── js/api.js                  # Wrapper fetch, toast, checkAuth, utilitaires
```

## Pages

### Publiques (sans connexion)
| URL | Template | Description |
|-----|----------|-------------|
| `/` | `landing.html` | Page de présentation de la plateforme |
| `/connexion` | `connexion.html` | Connexion — redirige selon le rôle |
| `/inscription` | `inscription.html` | Création de compte — redirige selon le rôle |

### Communes (connecté)
| URL | Template | Description |
|-----|----------|-------------|
| `/messagerie` | `messagerie.html` | Chat temps réel (SocketIO) |

### Étudiant
| URL | Template | Description |
|-----|----------|-------------|
| `/tableau-de-bord` | `dashboard.html` | Stats + sessions à venir + progression |
| `/matching` | `matching.html` | Recherche tuteurs avec créneaux et heures/matière |
| `/suivi` | `suivi.html` | Barres de progression + sessions passées |

### Tuteur
| URL | Template | Description |
|-----|----------|-------------|
| `/tuteur/dashboard` | `tuteur_dashboard.html` | Stats + sessions en attente + confirmation |
| `/tuteur/sessions` | `tuteur_sessions.html` | Toutes les sessions filtrables + notation progression |
| `/tuteur/matieres` | `tuteur_matieres.html` | Sélection + création de matières |
| `/tuteur/disponibilites` | `tuteur_disponibilites.html` | Créneaux hebdomadaires + heures par matière |

## Redirection automatique selon le rôle

Après connexion ou inscription :
- `etudiant` → `/tableau-de-bord`
- `tuteur` → `/tuteur/dashboard`

Les utilisateurs non connectés accédant à une page protégée sont redirigés vers `/connexion`.

## Sidebar adaptée par rôle

La sidebar affiche une navigation différente selon `user.role` :
- Étudiant : Tableau de bord, Trouver un tuteur, Messagerie, Suivi
- Tuteur : Tableau de bord, Mes sessions, Mes matières, Disponibilités, Messagerie

## api.js

Utilitaires globaux disponibles sur toutes les pages :

```js
API.get(url)              // GET fetch
API.post(url, body)       // POST fetch
API.put(url, body)        // PUT fetch
API.delete(url)           // DELETE fetch

toast(msg, type)          // Notification (success | error)
checkAuth()               // Vérifie la session, redirige vers / si non connecté
initiales(prenom, nom)    // "Amara Mbaye" → "AM"
couleurAv(role)           // Style CSS inline selon le rôle
formatDate(iso, opts)     // Date ISO → format fr-FR lisible
```

## Thème (style.css)

Variables CSS principales :

```css
--bg        #0f1117   /* fond principal */
--bg2       #171b26   /* sidebar, cards */
--bg3       #1e2333   /* inputs, rows */
--purple    #7c6ef7   /* couleur primaire */
--teal      #3ecfaa   /* succès, confirmé */
--text      #e8eaf0   /* texte principal */
--text2     #9aa0b8   /* texte secondaire */
--text3     #5a6080   /* texte désactivé */
```

Composants : `.card`, `.btn`, `.badge`, `.form-input`, `.form-select`,
`.stat-card`, `.session-row`, `.tutor-card`, `.progress-bar`, `.chat-layout`, `.toast`, `.modal-overlay`.

## Dépendances CDN

- [Sora + JetBrains Mono](https://fonts.google.com) — typographies
- [Tabler Icons](https://tabler.io/icons) — icônes (`ti ti-*`)
- [Socket.IO 4.7.5](https://socket.io) — chat temps réel (messagerie uniquement)

## Compatibilité

Testé avec Python 3.13. Le frontend ne nécessite aucun bundler ni framework JS.
