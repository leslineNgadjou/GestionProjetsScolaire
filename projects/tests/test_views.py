"""Tests des vues du module projects (acces et liste publique)."""

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from projects.models import Project

User = get_user_model()


class ProjectPublicListTests(TestCase):
    """Liste publique : uniquement les projets ouverts."""

    def setUp(self):
        self.teacher = User.objects.create_user(
            username='t_pub',
            email='t_pub@univ.fr',
            password='password123',
            role=User.Role.TEACHER,
        )
        Project.objects.create(
            title='Ouvert',
            description='d',
            teacher=self.teacher,
            domain='A',
            max_students=2,
            status=Project.Status.OPEN,
        )
        Project.objects.create(
            title='Ferme',
            description='d',
            teacher=self.teacher,
            domain='B',
            max_students=2,
            status=Project.Status.CLOSED,
        )

    def test_public_list_shows_only_open_projects(self):
        response = self.client.get(reverse('projects:list'))
        self.assertEqual(response.status_code, 200)
        titles = [p.title for p in response.context['project_list']]
        self.assertIn('Ouvert', titles)
        self.assertNotIn('Ferme', titles)


class ProjectPublicListPaginationTests(TestCase):
    """Pagination du catalogue public : 10 elements par page."""

    def setUp(self):
        self.teacher = User.objects.create_user(
            username='t_page',
            email='t_page@univ.fr',
            password='password123',
            role=User.Role.TEACHER,
        )
        for i in range(11):
            Project.objects.create(
                title=f'PaginerOpen{i}',
                description='d',
                teacher=self.teacher,
                domain='Dom',
                max_students=2,
                status=Project.Status.OPEN,
            )

    def test_first_page_has_ten_open_projects(self):
        response = self.client.get(reverse('projects:list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['paginator'].per_page, 10)
        self.assertEqual(len(response.context['project_list']), 10)


class ProjectPublicListSearchTests(TestCase):
    """Recherche par titre (parametre q)."""

    def setUp(self):
        self.teacher = User.objects.create_user(
            username='t_search',
            email='t_search@univ.fr',
            password='password123',
            role=User.Role.TEACHER,
        )
        Project.objects.create(
            title='AlphaZZUniqueToken',
            description='d',
            teacher=self.teacher,
            domain='A',
            max_students=2,
            status=Project.Status.OPEN,
        )
        Project.objects.create(
            title='BetaAutre',
            description='d',
            teacher=self.teacher,
            domain='B',
            max_students=2,
            status=Project.Status.OPEN,
        )

    def test_search_filters_by_title_fragment(self):
        response = self.client.get(
            reverse('projects:list'),
            {'q': 'ZZUniqueToken'},
        )
        self.assertEqual(response.status_code, 200)
        titles = [p.title for p in response.context['project_list']]
        self.assertIn('AlphaZZUniqueToken', titles)
        self.assertNotIn('BetaAutre', titles)


class ProjectPublicListDomainFilterTests(TestCase):
    """Filtre par domaine (parametre domain, insensible a la casse)."""

    def setUp(self):
        self.teacher = User.objects.create_user(
            username='t_domain',
            email='t_domain@univ.fr',
            password='password123',
            role=User.Role.TEACHER,
        )
        Project.objects.create(
            title='P1',
            description='d',
            teacher=self.teacher,
            domain='PhysiqueQuantique',
            max_students=2,
            status=Project.Status.OPEN,
        )
        Project.objects.create(
            title='P2',
            description='d',
            teacher=self.teacher,
            domain='Chimie',
            max_students=2,
            status=Project.Status.OPEN,
        )

    def test_filter_by_domain_exact_case_insensitive(self):
        response = self.client.get(
            reverse('projects:list'),
            {'domain': 'physiquequantique'},
        )
        self.assertEqual(response.status_code, 200)
        titles = [p.title for p in response.context['project_list']]
        self.assertIn('P1', titles)
        self.assertNotIn('P2', titles)


class ProjectTeacherStudentAccessTests(TestCase):
    """CRUD enseignant vs etudiant."""

    def setUp(self):
        self.client = Client()
        self.teacher = User.objects.create_user(
            username='t_crud',
            email='t_crud@univ.fr',
            password='password123',
            role=User.Role.TEACHER,
        )
        self.student = User.objects.create_user(
            username='s_crud',
            email='s_crud@univ.fr',
            password='password123',
            role=User.Role.STUDENT,
        )

    def test_teacher_can_create_project(self):
        self.client.login(username='t_crud', password='password123')
        url = reverse('projects:create')
        response = self.client.post(
            url,
            {
                'title': 'Nouveau cours',
                'description': 'Description longue du projet.',
                'domain': 'Informatique',
                'max_students': 3,
                'status': Project.Status.OPEN,
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            Project.objects.filter(
                title='Nouveau cours',
                teacher=self.teacher,
            ).exists(),
        )

    def test_student_cannot_access_create_project(self):
        self.client.login(username='s_crud', password='password123')
        response = self.client.get(reverse('projects:create'))
        self.assertEqual(response.status_code, 403)
