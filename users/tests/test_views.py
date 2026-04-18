"""Tests des vues utilisateurs (inscription)."""

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()

# Mot de passe conforme aux validateurs Django du projet
REGISTER_PASSWORD = 'UnMotDePasseSolide9!xyz'


class StudentRegistrationTests(TestCase):
    def test_register_creates_student_role_and_stores_email(self):
        response = self.client.post(
            reverse('register'),
            {
                'username': 'nouvel_etudiant',
                'email': 'nouvel.etudiant@univ.fr',
                'password1': REGISTER_PASSWORD,
                'password2': REGISTER_PASSWORD,
            },
        )
        self.assertEqual(response.status_code, 302)
        user = User.objects.get(username='nouvel_etudiant')
        self.assertEqual(user.role, User.Role.STUDENT)
        self.assertEqual(user.email, 'nouvel.etudiant@univ.fr')

    def test_register_rejects_duplicate_email(self):
        User.objects.create_user(
            username='deja_email',
            email='pris@univ.fr',
            password=REGISTER_PASSWORD,
            role=User.Role.STUDENT,
        )
        response = self.client.post(
            reverse('register'),
            {
                'username': 'autre_user',
                'email': 'pris@univ.fr',
                'password1': REGISTER_PASSWORD,
                'password2': REGISTER_PASSWORD,
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username='autre_user').exists())

    def test_register_rejects_invalid_email_format(self):
        response = self.client.post(
            reverse('register'),
            {
                'username': 'bad_mail_user',
                'email': 'pas-une-adresse',
                'password1': REGISTER_PASSWORD,
                'password2': REGISTER_PASSWORD,
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username='bad_mail_user').exists())

    def test_authenticated_user_redirected_from_register(self):
        User.objects.create_user(
            username='deja_la',
            email='deja@univ.fr',
            password=REGISTER_PASSWORD,
            role=User.Role.STUDENT,
        )
        self.client.login(username='deja_la', password=REGISTER_PASSWORD)
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('dashboard:index'))
