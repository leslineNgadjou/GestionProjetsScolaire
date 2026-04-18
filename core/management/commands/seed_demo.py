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
            domain='Data science',
            max_students=3,
            status=Project.Status.OPEN,
        )
        p_open_t2 = self._upsert_project(
            teacher=t2,
            title='[DEMO] Application web de suivi de stage',
            domain='Developpement web',
            max_students=2,
            status=Project.Status.OPEN,
        )
        p_closed = self._upsert_project(
            teacher=t1,
            title='[DEMO] Projet blockchain (archive)',
            domain='Blockchain',
            max_students=2,
            status=Project.Status.CLOSED,
        )
        p_done = self._upsert_project(
            teacher=t2,
            title='[DEMO] Systeme de recommandation — termine',
            domain='Machine learning',
            max_students=4,
            status=Project.Status.COMPLETED,
        )

        s1, s2, s3, s4 = students

        self._upsert_application(s1, p_open_t1, Application.Status.PENDING, MOTIVATION)
        self._upsert_application(s2, p_open_t1, Application.Status.ACCEPTED, MOTIVATION)
        self._upsert_application(s3, p_open_t2, Application.Status.PENDING, MOTIVATION)
        self._upsert_application(s4, p_open_t2, Application.Status.REJECTED, MOTIVATION)
        self._upsert_application(s1, p_open_t2, Application.Status.PENDING, MOTIVATION)
        self._upsert_application(s2, p_closed, Application.Status.ACCEPTED, MOTIVATION)

        self.stdout.write(self.style.SUCCESS('Donnees de demo chargees.'))
        self.stdout.write(f'  Admin : {admin.username} / {DEMO_PASSWORD}')
        self.stdout.write(f'  Enseignants : {t1.username}, {t2.username} / {DEMO_PASSWORD}')
        self.stdout.write(f'  Etudiants : {s1.username} … {s4.username} / {DEMO_PASSWORD}')

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

    def _upsert_project(self, teacher, title, domain, max_students, status):
        project, created = Project.objects.get_or_create(
            teacher=teacher,
            title=title,
            defaults={
                'description': f'Description de demonstration pour « {title} ».',
                'domain': domain,
                'max_students': max_students,
                'status': status,
            },
        )
        project.description = f'Description de demonstration pour « {title} ».'
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
