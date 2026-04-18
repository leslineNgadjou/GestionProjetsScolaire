"""Permissions dédiées à l'API REST (bonus examen)."""

from rest_framework.permissions import BasePermission


class IsTeacherUser(BasePermission):
    """Utilisateur authentifié avec le rôle enseignant (users.User.role)."""

    message = 'Seuls les enseignants peuvent créer un projet via l’API.'

    def has_permission(self, request, view):
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and getattr(user, 'is_teacher', False),
        )
