# Grille de conformité — sujet d’examen

Document de synthèse pour reprise par un correcteur. Légende : **Fait** | **Partiel** | **Manquant**.

| Exigence (sujet) | Statut | Fichiers / emplacement | Remarque |
|------------------|--------|-------------------------|----------|
| Authentification (login / logout) | **Fait** | `config/urls.py`, `templates/registration/login.html`, `settings.py` (`LOGIN_*`) | Redirection post-login vers le dashboard. |
| Rôles utilisateur (étudiant, enseignant, admin métier) | **Fait** | `users/models.py`, `core/mixins.py` | Distinct de `is_staff` / superuser Django. |
| CRUD projets réservé enseignant + propriétaire | **Fait** | `projects/views.py`, `projects/mixins.py` | Mise à jour / suppression : queryset filtré. |
| Liste publique projets **ouverts** uniquement | **Fait** | `projects/views.py` (`ProjectListView`) | |
| Recherche (titre) + filtre domaine + pagination | **Fait** | `projects/views.py`, `project_list.html` | 10 par page. |
| Détail projet | **Fait** | `projects/views.py`, `project_detail.html` | Enseignant voit aussi ses projets non ouverts. |
| Candidature étudiant sur projet ouvert | **Fait** | `applications/views.py`, `applications/models.py` | |
| Une candidature par couple étudiant / projet | **Fait** | `Application` `UniqueConstraint`, tests | |
| Liste / traitement candidatures par enseignant propriétaire | **Fait** | `applications/views.py`, `queryset` filtré | |
| Accepter / refuser + statuts pending / accepted / rejected | **Fait** | `AcceptApplicationView`, `RejectApplicationView` | |
| Limite `max_students` à l’acceptation | **Fait** | `applications/views.py`, `Project.can_accept_more_students()` | Transaction + `select_for_update`. |
| Notifications simulées | **Fait** | `django.contrib.messages`, `logging` logger `applications`, `settings.LOGGING` | Pas d’e-mail (conforme sujet « simulé »). |
| Dashboard par rôle (stats + UX) | **Fait** | `dashboard/views.py`, `dashboard/stats.py`, `templates/dashboard/index.html` | |
| Sécurité de base (CSRF, pas de secret en repo) | **Fait** | Templates POST, `.env`, `.gitignore` | Vérifier `DEBUG=False` en vraie prod. |
| Interface responsive (Bootstrap) | **Fait** | `templates/`, `static/css/app.css` | Grilles, cartes, navigation repliable. |
| Tests automatisés | **Fait** | `projects/tests/`, `applications/tests/`, `dashboard/tests/`, `users/tests/` | `python manage.py test …` |
| Données de démo / reproductible | **Fait** | `core/management/commands/seed_demo.py` | Comptes documentés dans `README.md`. |
| Documentation README | **Fait** | `README.md` | Installation, comptes, commandes, tests. |
| Déploiement production (HTTPS, serveur WSGI) | **Manquant** | — | Hors périmètre examen type « projet local » ; `runserver` documenté comme dev uniquement. |
| Internationalisation complète (i18n) | **Partiel** | `LANGUAGE_CODE = fr-fr` | Contenu principalement en français ; pas de fichiers `locale/`. |

## Passe sécurité / propreté (checklist rapide)

- [x] `SECRET_KEY` via `.env`, exemple dans `.env.example`
- [x] `.gitignore` : `.env`, `db.sqlite3`, `__pycache__`, `.venv`
- [x] Validation modèle (`full_clean` / formulaires) pour règles métier clés
- [x] Messages utilisateur sur succès / erreur / accès refusé
- [x] Pas de mot de passe en clair dans le dépôt (mot de passe démo **uniquement** pour `seed_demo`, documenté)

## Pistes bonus (non requises)

- Fichiers de traduction Django (`makemessages`)
- CI (GitHub Actions) exécutant `manage.py test`
- Couverture de code (`coverage run`)
- Démo filmée ou captures d’écran dans un dossier `docs/`
