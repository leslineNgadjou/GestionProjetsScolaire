"""Tests des vues candidatures (depot, doublon, acces enseignant)."""

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from applications.models import Application
from projects.models import Project

User = get_user_model()

MOTIVATION = (
    'Candidature de test avec une motivation suffisamment detaillee pour '
    'respecter la contrainte minimale du modele Application en tout cas.'
)


class StudentApplyTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.teacher = User.objects.create_user(
            username='t_apply',
            email='t_apply@univ.fr',
            password='password123',
            role=User.Role.TEACHER,
        )
        self.student = User.objects.create_user(
            username='s_apply',
            email='s_apply@univ.fr',
            password='password123',
            role=User.Role.STUDENT,
        )
        self.other_teacher = User.objects.create_user(
            username='t_other',
            email='t_other@univ.fr',
            password='password123',
            role=User.Role.TEACHER,
        )
        self.project = Project.objects.create(
            title='Projet ouvert',
            description='Description.',
            teacher=self.teacher,
            domain='Info',
            max_students=3,
            status=Project.Status.OPEN,
        )

    def test_student_can_apply_to_open_project(self):
        self.client.login(username='s_apply', password='password123')
        url = reverse('applications:create', kwargs={'project_id': self.project.pk})
        response = self.client.post(
            url,
            {'project': str(self.project.pk), 'motivation': MOTIVATION},
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            Application.objects.filter(
                student=self.student,
                project=self.project,
            ).exists(),
        )

    def test_student_cannot_apply_twice(self):
        Application.objects.create(
            student=self.student,
            project=self.project,
            motivation=MOTIVATION,
            status=Application.Status.PENDING,
        )
        self.client.login(username='s_apply', password='password123')
        url = reverse('applications:create', kwargs={'project_id': self.project.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, self.project.get_absolute_url())


class TeacherApplicationAccessTests(TestCase):
    """Un enseignant ne traite que les candidatures de ses projets."""

    def setUp(self):
        self.client = Client()
        self.owner = User.objects.create_user(
            username='t_owner',
            email='t_owner@univ.fr',
            password='password123',
            role=User.Role.TEACHER,
        )
        self.intruder = User.objects.create_user(
            username='t_intr',
            email='t_intr@univ.fr',
            password='password123',
            role=User.Role.TEACHER,
        )
        self.student = User.objects.create_user(
            username='s_own',
            email='s_own@univ.fr',
            password='password123',
            role=User.Role.STUDENT,
        )
        self.project = Project.objects.create(
            title='Projet du owner',
            description='d',
            teacher=self.owner,
            domain='X',
            max_students=5,
            status=Project.Status.OPEN,
        )
        self.application = Application.objects.create(
            student=self.student,
            project=self.project,
            motivation=MOTIVATION,
            status=Application.Status.PENDING,
        )

    def test_other_teacher_gets_404_on_accept(self):
        self.client.login(username='t_intr', password='password123')
        url = reverse('applications:accept', kwargs={'pk': self.application.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)

    def test_owner_can_accept(self):
        self.client.login(username='t_owner', password='password123')
        url = reverse('applications:accept', kwargs={'pk': self.application.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.application.refresh_from_db()
        self.assertEqual(self.application.status, Application.Status.ACCEPTED)
