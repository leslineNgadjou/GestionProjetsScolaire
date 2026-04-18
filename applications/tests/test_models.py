"""Tests du modele Application."""

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase

from applications.models import Application
from projects.models import Project

User = get_user_model()

MOTIVATION = (
    'Texte de motivation de demonstration avec assez de caracteres pour valider '
    'le modele sans erreur de validation cote champ.'
)


class ApplicationModelTests(TestCase):
    def setUp(self):
        self.teacher = User.objects.create_user(
            username='t_app',
            email='t_app@univ.fr',
            password='password123',
            role=User.Role.TEACHER,
        )
        self.student = User.objects.create_user(
            username='s_app',
            email='s_app@univ.fr',
            password='password123',
            role=User.Role.STUDENT,
        )
        self.project_open = Project.objects.create(
            title='PO',
            description='d',
            teacher=self.teacher,
            domain='Dom',
            max_students=5,
            status=Project.Status.OPEN,
        )
        self.project_closed = Project.objects.create(
            title='PC',
            description='d',
            teacher=self.teacher,
            domain='Dom',
            max_students=5,
            status=Project.Status.CLOSED,
        )

    def test_unique_student_per_project(self):
        Application.objects.create(
            student=self.student,
            project=self.project_open,
            motivation=MOTIVATION,
            status=Application.Status.PENDING,
        )
        duplicate = Application(
            student=self.student,
            project=self.project_open,
            motivation=MOTIVATION,
            status=Application.Status.PENDING,
        )
        with self.assertRaises(IntegrityError):
            duplicate.save()

    def test_new_application_on_closed_project_raises_in_clean(self):
        app = Application(
            student=self.student,
            project=self.project_closed,
            motivation=MOTIVATION,
            status=Application.Status.PENDING,
        )
        with self.assertRaises(ValidationError):
            app.full_clean()
