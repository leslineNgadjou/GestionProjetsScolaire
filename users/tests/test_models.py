"""Tests leger du modele utilisateur personnalise."""

from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.test import TestCase

User = get_user_model()


class UserModelTests(TestCase):
    def test_role_helpers(self):
        s = User.objects.create_user(
            username='s_u',
            email='s_u@univ.fr',
            password='password123',
            role=User.Role.STUDENT,
        )
        t = User.objects.create_user(
            username='t_u',
            email='t_u@univ.fr',
            password='password123',
            role=User.Role.TEACHER,
        )
        self.assertTrue(s.is_student)
        self.assertFalse(s.is_teacher)
        self.assertTrue(t.is_teacher)
        self.assertFalse(t.is_platform_admin)

    def test_email_unique_enforced_by_database(self):
        User.objects.create_user(
            username='uniq_a',
            email='meme.email@univ.fr',
            password='password123',
            role=User.Role.STUDENT,
        )
        with self.assertRaises(IntegrityError):
            User.objects.create_user(
                username='uniq_b',
                email='meme.email@univ.fr',
                password='password123',
                role=User.Role.STUDENT,
            )
