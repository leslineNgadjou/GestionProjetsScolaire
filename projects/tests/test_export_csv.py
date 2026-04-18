"""Tests export CSV des projets enseignant (bonus)."""

import csv
import io

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from projects.models import Project

User = get_user_model()


class TeacherProjectsExportCSVTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.teacher = User.objects.create_user(
            username='t_csv',
            email='t_csv@univ.fr',
            password='password123',
            role=User.Role.TEACHER,
        )
        self.student = User.objects.create_user(
            username='s_csv',
            email='s_csv@univ.fr',
            password='password123',
            role=User.Role.STUDENT,
        )
        self.project = Project.objects.create(
            title='Pour CSV',
            description='d',
            teacher=self.teacher,
            domain='Bio',
            max_students=5,
            status=Project.Status.OPEN,
        )

    def test_teacher_downloads_csv_with_own_projects(self):
        self.client.login(username='t_csv', password='password123')
        response = self.client.get(reverse('projects:export_csv'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('text/csv', response['Content-Type'])
        self.assertIn('attachment', response['Content-Disposition'])
        self.assertIn('mes_projets_export.csv', response['Content-Disposition'])
        body = response.content.decode('utf-8')
        self.assertIn('id,title,domain,status,max_students,created_at', body)
        self.assertIn('Pour CSV', body)
        self.assertIn('Bio', body)

    def test_csv_rows_coherent_with_database(self):
        self.client.login(username='t_csv', password='password123')
        response = self.client.get(reverse('projects:export_csv'))
        reader = csv.reader(io.StringIO(response.content.decode('utf-8')))
        rows = list(reader)
        self.assertEqual(
            rows[0],
            ['id', 'title', 'domain', 'status', 'max_students', 'created_at'],
        )
        self.assertEqual(len(rows), 2)
        _id, title, domain, status, max_students, created_at = rows[1]
        self.assertEqual(_id, str(self.project.pk))
        self.assertEqual(title, 'Pour CSV')
        self.assertEqual(domain, 'Bio')
        self.assertEqual(status, Project.Status.OPEN)
        self.assertEqual(max_students, '5')
        self.assertEqual(created_at, self.project.created_at.isoformat())

    def test_csv_excludes_other_teacher_projects(self):
        other = User.objects.create_user(
            username='t_autre',
            email='t_autre@univ.fr',
            password='password123',
            role=User.Role.TEACHER,
        )
        Project.objects.create(
            title='Projet autre enseignant',
            description='x',
            teacher=other,
            domain='Chimie',
            max_students=2,
            status=Project.Status.OPEN,
        )
        self.client.login(username='t_csv', password='password123')
        response = self.client.get(reverse('projects:export_csv'))
        body = response.content.decode('utf-8')
        self.assertNotIn('Projet autre enseignant', body)
        self.assertNotIn('Chimie', body)

    def test_student_cannot_access_export_csv(self):
        self.client.login(username='s_csv', password='password123')
        response = self.client.get(reverse('projects:export_csv'))
        self.assertEqual(response.status_code, 403)
