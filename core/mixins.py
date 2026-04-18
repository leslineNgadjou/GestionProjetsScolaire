"""Mixins transverses pour le controle d'acces (reutilisables par plusieurs apps)."""

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect


class TeacherRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """
    Reserve la vue aux utilisateurs authentifies dont le role est enseignant.

    Les utilisateurs connectes mais non enseignants sont rediriges vers la liste
    publique des projets avec un message d'erreur.
    """

    def test_func(self):
        user = self.request.user
        if not user.is_authenticated:
            return False
        return getattr(user, 'role', None) == user.Role.TEACHER

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        messages.error(
            self.request,
            "Accès réservé aux enseignants.",
        )
        return redirect('projects:list')


class StudentRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """
    Reserve la vue aux utilisateurs authentifies dont le role est etudiant.

    Les autres roles connectes sont rediriges vers la liste publique des projets.
    """

    def test_func(self):
        user = self.request.user
        if not user.is_authenticated:
            return False
        return getattr(user, 'is_student', False)

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        messages.error(
            self.request,
            'Accès réservé aux étudiants.',
        )
        return redirect('projects:list')
