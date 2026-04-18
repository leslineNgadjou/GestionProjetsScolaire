# Gestion de projets étudiants

Plateforme web **Django** pour la gestion de **projets universitaires** : publication par les enseignants, candidatures par les étudiants, traitement des dossiers et tableaux de bord par rôle (étudiant, enseignant, administrateur métier).

## Présentation

- **Enseignants** : créent et gèrent leurs projets (CRUD), consultent les candidatures reçues, acceptent ou refusent (dans la limite des places `max_students`).
- **Étudiants** : parcourent le catalogue public (projets **ouverts**), postulent une seule fois par projet, suivent le statut de leurs candidatures.
- **Administrateur métier** : tableau de bord avec statistiques globales (utilisateurs, projets, candidatures).

## Stack technique

| Élément | Choix |
|--------|--------|
| Framework | Django 5.2 |
| Base de données | SQLite (développement / démo) |
| Front | Templates Django + **Bootstrap 5** |
| API (bonus) | **Django REST framework** (`/api/…`) |
| Config sensible | `python-dotenv` (fichier `.env`) |
| Police | Plus Jakarta Sans (Google Fonts) |

## Prérequis

- Python **3.11+** (recommandé)
- Un environnement virtuel

## Installation

### 1. Cloner et se placer dans le projet

```bash
cd GestionProjetsScolaire
```

### 2. Environnement virtuel

**Windows (PowerShell)**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**Linux / macOS**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Dépendances

```bash
pip install -r requirements.txt
```

### 4. Fichier `.env`

Copier l’exemple et définir au minimum une **clé secrète** :

- **Windows :** `copy .env.example .env`
- **Linux / macOS :** `cp .env.example .env`

Éditer `.env` :

```env
SECRET_KEY=votre-cle-longue-et-aleatoire
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

> Sans `SECRET_KEY`, le projet refuse de démarrer (`ImproperlyConfigured`).

### 5. Migrations

```bash
python manage.py migrate
```

> La migration `users.0002_user_email_unique` impose l’**unicité de l’e-mail** (index en base). Si d’anciennes lignes avaient le même e-mail ou un e-mail vide, elles sont corrigées automatiquement avant l’index (voir la migration).

### 6. Données de démonstration (recommandé)

Commande personnalisée **idempotente** (rejouable avant une soutenance) :

```bash
python manage.py seed_demo
```

Crée notamment :

- 1 administrateur (`admin@univ.fr`)
- 2 enseignants (`teacher@univ.fr`, `teacher2@univ.fr`)
- 4 étudiants (`student@univ.fr`, …)
- Plusieurs projets (ouverts, fermés, terminés)
- Des candidatures aux statuts variés

**Mot de passe unique pour tous ces comptes de démo :** `password123`

### 7. Lancer le serveur de développement

```bash
python manage.py runserver
```

Ouvrir [http://127.0.0.1:8000/](http://127.0.0.1:8000/) — après connexion, redirection vers le **tableau de bord**.

## Comptes de test (démo)

| Rôle | Identifiant | Mot de passe |
|------|-------------|--------------|
| Enseignant (principal) | `teacher@univ.fr` | `password123` |
| Étudiant (principal) | `student@univ.fr` | `password123` |
| Administrateur | `admin@univ.fr` | `password123` |

Les autres comptes créés par `seed_demo` utilisent le même mot de passe ; voir la sortie de la commande pour la liste complète.

## Fonctionnalités principales

- Authentification Django, rôles sur `users.User` (étudiant / enseignant / admin métier) ; **inscription étudiant** sur `/register/` (nom d’utilisateur, **e-mail validé**, **unicité garantie en base de données**, mot de passe avec validateurs Django, rôle étudiant uniquement).
- **Projets** : liste publique filtrée (statut **ouvert**), recherche, filtre domaine, pagination ; détail ; CRUD réservé à l’enseignant propriétaire.
- **Candidatures** : dépôt sur projet ouvert, liste « mes candidatures », réception et traitement par l’enseignant concerné, respect de `max_students` à l’acceptation.
- **Dashboard** : statistiques et raccourcis selon le rôle.
- **Notifications simulées** : messages Django + logs (`applications` logger, console en développement).
- **Bonus examen** : API REST minimale sur les projets ; export **CSV** des projets pour l’enseignant connecté.

### API REST (projets)

Préfixe : **`/api/`** (voir `projects/api_views.py`, `projects/serializers.py`).

| Méthode | URL | Accès | Description |
|--------|-----|--------|-------------|
| GET | `/api/projects/` | Public (lecture) | Liste **paginée** (10 par page) : projets **ouverts** ; si connecté en tant qu’**enseignant**, inclut aussi **ses** projets (tous statuts). |
| GET | `/api/projects/<id>/` | Public (lecture) | Détail si projet ouvert ou si vous êtes l’**enseignant** propriétaire. |
| POST | `/api/projects/` | **Enseignant authentifié** | Création JSON (`title`, `description`, `domain`, `max_students`, `status`) ; l’enseignant est celui du compte. |

Authentification pour POST (et lecture étendue enseignant) : **session** (navigateur connecté) ou **HTTP Basic** (ex. `curl`).

**Exemples (serveur local)**

```bash
# Liste (anonyme)
curl -s http://127.0.0.1:8000/api/projects/ | python -m json.tool

# Détail
curl -s http://127.0.0.1:8000/api/projects/1/ | python -m json.tool

# Création (enseignant) — Basic auth
curl -s -u teacher@univ.fr:password123 -H "Content-Type: application/json" \
  -d "{\"title\":\"Sujet API\",\"description\":\"Description longue du sujet cree par curl pour valider l API.\",\"domain\":\"Info\",\"max_students\":3,\"status\":\"open\"}" \
  http://127.0.0.1:8000/api/projects/
```

> Avec **SessionAuthentication** depuis le navigateur, un POST doit inclure le jeton **CSRF** Django ; pour des tests rapides, privilégier **Basic auth** ou `APIClient` / `force_authenticate` dans les tests.

### Export CSV (mes projets)

- **URL** : `/projects/my/export-csv/` (nom d’URL Django : `projects:export_csv`).
- **Accès** : **enseignant** connecté uniquement (ses propres lignes ; **403** pour les autres rôles).
- **Colonnes** : `id`, `title`, `domain`, `status`, `max_students`, `created_at`.
- **Fichier téléchargé** : `mes_projets_export.csv`.
- **UI** : bouton « Export CSV » sur la page **Mes projets** (`/projects/my/`).

Téléchargement : ouvrir l’URL connecté en enseignant ou utiliser un lien depuis « Mes projets ».

## Structure du projet (aperçu)

```
GestionProjetsScolaire/
├── config/              # settings, urls, wsgi, asgi
├── core/                # accueil, mixins partagés, commande seed_demo
├── users/               # modèle User personnalisé
├── projects/            # modèle Project, vues, formulaires
├── applications/        # modèle Application (candidatures)
├── dashboard/           # tableau de bord par rôle (+ stats.py)
├── templates/
├── static/
├── manage.py
├── requirements.txt
├── .env.example
├── CONFORMITE.md        # grille de conformité au sujet d’examen
└── README.md
```

## Commandes utiles

| Commande | Description |
|----------|-------------|
| `python manage.py runserver` | Serveur de développement |
| `python manage.py migrate` | Appliquer les migrations |
| `python manage.py createsuperuser` | Compte super-utilisateur (admin Django) |
| `python manage.py seed_demo` | Jeu de données de démonstration |
| `python manage.py check` | Vérifications système Django |

## Tests automatisés

Les tests utilisent une base SQLite **temporaire**. Il faut que la variable d’environnement **`SECRET_KEY`** soit définie (comme pour l’app).

**Windows PowerShell**

```powershell
$env:SECRET_KEY = "test-secret-key"
python manage.py test projects applications dashboard users
```

**Linux / macOS**

```bash
SECRET_KEY=test-secret-key python manage.py test projects applications dashboard users
```

Couverture indicative : modèles `Project` / `Application`, liste publique, création de projet (enseignant), refus d’accès étudiant au CRUD projet, candidature, doublon, acceptation réservée au bon enseignant, dashboard par rôle, helpers utilisateur, **API REST** (GET liste, POST enseignant / refus étudiant), **export CSV** enseignant.

## Sécurité (rappels examen)

- `SECRET_KEY` et secrets dans `.env` — **ne pas commiter** `.env` (voir `.gitignore`).
- Formulaires POST protégés par **CSRF** (`{% csrf_token %}`).
- Contrôles d’accès par **mixins** (enseignant / étudiant) et **querysets** restreints.
- Mots de passe **jamais** en clair en base (hash Django).

## Licence / usage

Projet pédagogique — usage dans le cadre d’un examen ou d’une formation.
