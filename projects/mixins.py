"""Mixins specifiques a l'app projects."""

from core.mixins import TeacherRequiredMixin

from .models import Project


class TeacherOwnedProjectsMixin(TeacherRequiredMixin):
    """
    Restreint le queryset aux projets dont l'enseignant connecte est proprietaire.

    A utiliser avec les vues mono-objet (mise a jour, suppression).
    """

    def get_queryset(self):
        return Project.objects.filter(teacher=self.request.user).select_related(
            'teacher',
        )
