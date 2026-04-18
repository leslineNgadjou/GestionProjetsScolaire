"""Tests du tableau de bord (login requis, contenu par role)."""

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()


class DashboardViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.student = User.objects.create_user(
            username='s_dash',
            email='s_dash@univ.fr',
            password='password123',
            role=User.Role.STUDENT,
        )
        self.teacher = User.objects.create_user(
            username='t_dash',
            email='t_dash@univ.fr',
            password='password123',
            role=User.Role.TEACHER,
        )
        self.admin = User.objects.create_user(
            username='a_dash',
            email='a_dash@univ.fr',
            password='password123',
            role=User.Role.ADMIN,
        )

    def test_anonymous_redirected_to_login(self):
        response = self.client.get(reverse('dashboard:index'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)

    def test_student_sees_student_dashboard(self):
        self.client.login(username='s_dash', password='password123')
        response = self.client.get(reverse('dashboard:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'étudiant', status_code=200)

    def test_teacher_sees_teacher_dashboard(self):
        self.client.login(username='t_dash', password='password123')
        response = self.client.get(reverse('dashboard:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'enseignant', status_code=200)

    def test_platform_admin_sees_admin_dashboard(self):
        self.client.login(username='a_dash', password='password123')
        response = self.client.get(reverse('dashboard:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'administrateur', status_code=200)
        self.assertContains(response, 'Synthèse visuelle', status_code=200)
        self.assertContains(response, 'admin-chart-users-data', status_code=200)
