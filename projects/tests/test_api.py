"""Tests API REST bonus (liste / creation projets)."""

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase

from projects.models import Project

User = get_user_model()


class ProjectAPITests(APITestCase):
    def setUp(self):
        self.teacher = User.objects.create_user(
            username='t_api',
            email='t_api@univ.fr',
            password='password123',
            role=User.Role.TEACHER,
        )
        self.student = User.objects.create_user(
            username='s_api',
            email='s_api@univ.fr',
            password='password123',
            role=User.Role.STUDENT,
        )
        self.project_open = Project.objects.create(
            title='Ouvert API',
            description='Description du projet ouvert pour les tests API.',
            teacher=self.teacher,
            domain='Info',
            max_students=3,
            status=Project.Status.OPEN,
        )
        self.project_closed = Project.objects.create(
            title='Ferme API',
            description='Description du projet ferme pour les tests API.',
            teacher=self.teacher,
            domain='Archives',
            max_students=2,
            status=Project.Status.CLOSED,
        )

    def test_get_projects_list_anonymous_only_open(self):
        url = reverse('projects_api:project-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('results', response.data)
        ids = {item['id'] for item in response.data['results']}
        self.assertIn(self.project_open.pk, ids)
        self.assertNotIn(self.project_closed.pk, ids)
        self.assertEqual(response.data['results'][0].get('teacher_username'), 't_api')

    def test_post_project_as_teacher_creates(self):
        self.client.force_authenticate(user=self.teacher)
        url = reverse('projects_api:project-list')
        payload = {
            'title': 'Cree via API',
            'description': 'Description detaillee du projet cree via API REST.',
            'domain': 'Data',
            'max_students': 4,
            'status': Project.Status.OPEN,
        }
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, 201)
        created = Project.objects.get(title='Cree via API')
        self.assertEqual(created.teacher_id, self.teacher.pk)

    def test_post_project_as_student_forbidden(self):
        self.client.force_authenticate(user=self.student)
        url = reverse('projects_api:project-list')
        payload = {
            'title': 'Tentative etudiant',
            'description': 'Description detaillee pour test refus API etudiant.',
            'domain': 'X',
            'max_students': 2,
            'status': Project.Status.OPEN,
        }
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, 403)
        self.assertFalse(Project.objects.filter(title='Tentative etudiant').exists())
