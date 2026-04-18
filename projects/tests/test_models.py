"""Tests du modele Project."""

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from applications.models import Application
from projects.models import Project

User = get_user_model()

MOTIVATION_MIN = (
    'Motivation de test suffisamment longue pour passer la validation minimale '
    'des vingt caracteres requis par le modele Application.'
)


class ProjectModelTests(TestCase):
    """Validations et methodes utilitaires."""

    def setUp(self):
        self.teacher = User.objects.create_user(
            username='t_model',
            email='t_model@univ.fr',
            password='password123',
            role=User.Role.TEACHER,
        )
        self.student = User.objects.create_user(
            username='s_model',
            email='s_model@univ.fr',
            password='password123',
            role=User.Role.STUDENT,
        )

    def test_clean_rejects_non_teacher_as_teacher_fk(self):
        project = Project(
            title='  Titre valide  ',
            description='Desc',
            teacher=self.student,
            domain='Info',
            max_students=2,
            status=Project.Status.OPEN,
        )
        with self.assertRaises(ValidationError):
            project.full_clean()

    def test_clean_strips_title(self):
        project = Project(
            title='  Mon titre  ',
            description='Desc',
            teacher=self.teacher,
            domain='Info',
            max_students=2,
            status=Project.Status.OPEN,
        )
        project.full_clean()
        self.assertEqual(project.title, 'Mon titre')

    def test_accepted_applications_count(self):
        project = Project.objects.create(
            title='P1',
            description='D',
            teacher=self.teacher,
            domain='Dom',
            max_students=5,
            status=Project.Status.OPEN,
        )
        self.assertEqual(project.accepted_applications_count(), 0)
        Application.objects.create(
            student=self.student,
            project=project,
            motivation=MOTIVATION_MIN,
            status=Application.Status.ACCEPTED,
        )
        Application.objects.create(
            student=User.objects.create_user(
                username='s2',
                email='s2@u.fr',
                password='password123',
                role=User.Role.STUDENT,
            ),
            project=project,
            motivation=MOTIVATION_MIN,
            status=Application.Status.PENDING,
        )
        self.assertEqual(project.accepted_applications_count(), 1)
        self.assertTrue(project.can_accept_more_students())
