"""Peuple la base avec des comptes et donnees de demonstration (idempotent)."""

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from applications.models import Application
from projects.models import Project

User = get_user_model()

DEMO_PASSWORD = 'password123'

MOTIVATION = (
    'Je suis tres motive par ce sujet et j’ai deja travaille sur des projets '
    'similaires en equipe. Je souhaite approfondir mes competences.'
)

MOTIVATION_SHORT = (
    'Projet aligne avec mon parcours : je souhaite contribuer et apprendre '
    'sur la duree du semestre.'
)


class Command(BaseCommand):
    help = (
        'Charge des donnees de demo (admin, enseignants, etudiants, projets, '
        'candidatures). Rejouable : met a jour mots de passe et champs cles.'
    )

    def handle(self, *args, **options):
        admin = self._upsert_user(
            username='admin@univ.fr',
            email='admin@univ.fr',
            role=User.Role.ADMIN,
            is_staff=True,
            is_superuser=True,
            first_name='Admin',
            last_name='Plateforme',
        )
        t1 = self._upsert_user(
            username='teacher@univ.fr',
            email='teacher@univ.fr',
            role=User.Role.TEACHER,
            first_name='Claire',
            last_name='Durand',
        )
        t2 = self._upsert_user(
            username='teacher2@univ.fr',
            email='teacher2@univ.fr',
            role=User.Role.TEACHER,
            first_name='Marc',
            last_name='Lefevre',
        )
        students = []
        for i, (un, em, fn, ln) in enumerate(
            [
                ('student@univ.fr', 'student@univ.fr', 'Alex', 'Martin'),
                ('student2@univ.fr', 'student2@univ.fr', 'Sam', 'Bernard'),
                ('student3@univ.fr', 'student3@univ.fr', 'Lee', 'Nguyen'),
                ('student4@univ.fr', 'student4@univ.fr', 'Nina', 'Roux'),
            ],
            start=1,
        ):
            students.append(
                self._upsert_user(
                    username=un,
                    email=em,
                    role=User.Role.STUDENT,
                    first_name=fn,
                    last_name=ln,
                )
            )

        p_open_t1 = self._upsert_project(
            teacher=t1,
            title='[DEMO] Analyse de donnees pedagogiques',
            domain='Science des donnees',
            max_students=4,
            status=Project.Status.OPEN,
            description_extra=(
                'Tableaux de bord pour suivre l’engagement des groupes, exports CSV '
                'et indicateurs par enseignant. Idéal pour valider la chaîne ETL et la '
                'visualisation sous contrainte RGPD (données anonymisées).'
            ),
        )
        p_open_t2 = self._upsert_project(
            teacher=t2,
            title='[DEMO] Application web de suivi de stage',
            domain='Developpement web',
            max_students=3,
            status=Project.Status.OPEN,
            description_extra=(
                'Stack Django / API REST : conventions de code, revues et livraisons '
                'par sprints. Les étudiants intègrent auth, rôles et notifications '
                'simulées pour coller à un produit SaaS interne.'
            ),
        )
        p_open_t1b = self._upsert_project(
            teacher=t1,
            title='[DEMO] Tableau de bord carbone pour le campus',
            domain='Science des donnees',
            max_students=3,
            status=Project.Status.OPEN,
            description_extra=(
                'Modélisation des flux énergétiques bâtiments, jeux de données '
                'ouverts et scénarios “what-if”. Restitution attendue : rapport + '
                'prototype de calcul des indicateurs.'
            ),
        )
        p_open_t1c = self._upsert_project(
            teacher=t1,
            title='[DEMO] API securisee pour emplois du temps',
            domain='Developpement web',
            max_students=4,
            status=Project.Status.OPEN,
            description_extra=(
                'Conception d’une API versionnée (pagination, erreurs structurées) et '
                'd’un client léger. Thèmes : OAuth2 simplifié, quotas et journaux '
                'd’audit pour l’administration.'
            ),
        )
        p_open_t1d = self._upsert_project(
            teacher=t1,
            title='[DEMO] Refonte UX du portail etudiant',
            domain='UX et design produit',
            max_students=3,
            status=Project.Status.OPEN,
            description_extra=(
                'Interviews utilisateurs, parcours critiques et maquettes testables. '
                'Livrables : design system minimal, tests d’utilisabilité et backlog '
                'priorisé pour une équipe dev.'
            ),
        )
        p_open_t2b = self._upsert_project(
            teacher=t2,
            title="[DEMO] Detection d'anomalies sur journaux SI",
            domain='Cybersecurite',
            max_students=3,
            status=Project.Status.OPEN,
            description_extra=(
                'Jeux de logs synthétiques, règles de détection et scoring de risque. '
                'Introduction à la corrélation d’événements et à la restitution pour '
                'un SOC pédagogique.'
            ),
        )
        p_open_t2c = self._upsert_project(
            teacher=t2,
            title='[DEMO] Capteurs LoRa pour agriculture urbaine',
            domain='IoT et systemes embarques',
            max_students=4,
            status=Project.Status.OPEN,
            description_extra=(
                'Acquisition bas débit, passerelle et télémétrie vers une base '
                'série temporelle. Focus robustesse, autonomie batterie et '
                'visualisation des séries sur plusieurs parcelles fictives.'
            ),
        )
        p_open_t2d = self._upsert_project(
            teacher=t2,
            title='[DEMO] Pipeline NLP pour revues de litterature',
            domain='Machine learning',
            max_students=3,
            status=Project.Status.OPEN,
            description_extra=(
                'Extraction d’entités, clustering thématique et synthèses assistées. '
                'Données : corpus bibliographique public filtré. Éthique et biais des '
                'modèles discutés en restitution.'
            ),
        )
        p_open_t2e = self._upsert_project(
            teacher=t2,
            title='[DEMO] Serious game de revision L3 mathematiques',
            domain='Developpement web',
            max_students=5,
            status=Project.Status.OPEN,
            description_extra=(
                'Gameplay court, progression par compétences et tableau de bord '
                'enseignant. Front responsive (Bootstrap) et suivi des scores pour '
                'ajuster la difficulté.'
            ),
        )

        p_closed = self._upsert_project(
            teacher=t1,
            title='[DEMO] Projet blockchain (archive)',
            domain='Blockchain',
            max_students=2,
            status=Project.Status.CLOSED,
            description_extra=(
                'Archive de demo : smart-contracts expliqués, pas de mise en prod. '
                'Conservé pour tester l’affichage des projets fermés côté enseignant.'
            ),
        )
        p_done = self._upsert_project(
            teacher=t2,
            title='[DEMO] Systeme de recommandation — termine',
            domain='Machine learning',
            max_students=4,
            status=Project.Status.COMPLETED,
            description_extra=(
                'Campagne clôturée : jeux de données scoring offline et métriques '
                'de ranking. Sert de référence “terminé” dans les filtres enseignant.'
            ),
        )

        s1, s2, s3, s4 = students

        self._upsert_application(s1, p_open_t1, Application.Status.PENDING, MOTIVATION)
        self._upsert_application(s2, p_open_t1, Application.Status.ACCEPTED, MOTIVATION)
        self._upsert_application(s3, p_open_t2, Application.Status.PENDING, MOTIVATION)
        self._upsert_application(s4, p_open_t2, Application.Status.REJECTED, MOTIVATION)
        self._upsert_application(s1, p_open_t2, Application.Status.PENDING, MOTIVATION_SHORT)
        self._upsert_application(s2, p_closed, Application.Status.ACCEPTED, MOTIVATION)

        self._upsert_application(s3, p_open_t1b, Application.Status.PENDING, MOTIVATION_SHORT)
        self._upsert_application(s4, p_open_t1c, Application.Status.PENDING, MOTIVATION)
        self._upsert_application(s1, p_open_t2b, Application.Status.PENDING, MOTIVATION_SHORT)
        self._upsert_application(s2, p_open_t2c, Application.Status.ACCEPTED, MOTIVATION)
        self._upsert_application(s3, p_open_t2d, Application.Status.PENDING, MOTIVATION)
        self._upsert_application(s4, p_open_t1d, Application.Status.PENDING, MOTIVATION_SHORT)
        self._upsert_application(s1, p_open_t2e, Application.Status.PENDING, MOTIVATION)

        self.stdout.write(self.style.SUCCESS('Donnees de demo chargees.'))
        self.stdout.write(f'  Admin : {admin.username} / {DEMO_PASSWORD}')
        self.stdout.write(f'  Enseignants : {t1.username}, {t2.username} / {DEMO_PASSWORD}')
        self.stdout.write(f'  Etudiants : {s1.username} ... {s4.username} / {DEMO_PASSWORD}')
        self.stdout.write(
            self.style.NOTICE(
                '  Catalogue public : 9 projets ouverts (filtres domaine / recherche).'
            )
        )

    def _upsert_user(self, username, email, role, **extra):
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': email,
                'role': role,
                **extra,
            },
        )
        user.email = email
        user.role = role
        for k, v in extra.items():
            setattr(user, k, v)
        user.set_password(DEMO_PASSWORD)
        user.save()
        action = 'cree' if created else 'mis a jour'
        self.stdout.write(f'  Utilisateur {action} : {username} ({role})')
        return user

    def _upsert_project(
        self,
        teacher,
        title,
        domain,
        max_students,
        status,
        *,
        description_extra=None,
    ):
        if description_extra:
            description = (
                f'{description_extra} Contexte académique : équipe de 2 à 4 étudiants, '
                f'restitution sous forme de démo et rapport court (≈ 15 pages).'
            )
        else:
            description = f'Description de demonstration pour « {title} ».'
        project, created = Project.objects.get_or_create(
            teacher=teacher,
            title=title,
            defaults={
                'description': description,
                'domain': domain,
                'max_students': max_students,
                'status': status,
            },
        )
        project.description = description
        project.domain = domain
        project.max_students = max_students
        project.status = status
        project.save()
        action = 'cree' if created else 'mis a jour'
        self.stdout.write(f'  Projet {action} : {title}')
        return project

    def _upsert_application(self, student, project, status, motivation):
        app, created = Application.objects.update_or_create(
            student=student,
            project=project,
            defaults={
                'motivation': motivation,
                'status': status,
            },
        )
        action = 'cree' if created else 'mis a jour'
        self.stdout.write(
            f'  Candidature {action} : {student.username} -> {project.title} ({status})'
        )
        return app
