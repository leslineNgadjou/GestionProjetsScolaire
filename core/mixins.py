"""Mixins transverses pour le controle d'acces (reutilisables par plusieurs apps)."""

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied


class TeacherRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """
    Reserve la vue aux utilisateurs authentifies dont le role est enseignant.

    Utilisateur connecte avec un autre role : 403 (PermissionDenied).
    Anonyme : redirection vers la page de connexion (comportement LoginRequiredMixin).
    """

    def test_func(self):
        user = self.request.user
        if not user.is_authenticated:
            return False
        return getattr(user, 'role', None) == user.Role.TEACHER

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        raise PermissionDenied(
            'Accès réservé aux enseignants.',
        )


class StudentRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """
    Reserve la vue aux utilisateurs authentifies dont le role est etudiant.

    Utilisateur connecte avec un autre role : 403 (PermissionDenied).
    """

    def test_func(self):
        user = self.request.user
        if not user.is_authenticated:
            return False
        return getattr(user, 'is_student', False)

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        raise PermissionDenied(
            'Accès réservé aux étudiants.',
        )
