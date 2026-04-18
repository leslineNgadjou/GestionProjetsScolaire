"""Vues du tableau de bord : contenu adapte au role (etudiant, enseignant, admin)."""

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from . import stats


class DashboardIndexView(LoginRequiredMixin, TemplateView):
    """
    Page d’accueil connectee : statistiques et raccourcis selon users.User.role.

    Les agregations sont preparees dans ``dashboard.stats`` pour garder la vue legere.
    """

    template_name = 'dashboard/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        if user.is_student:
            context.update(stats.student_dashboard_context(user))
        elif user.is_teacher:
            context.update(stats.teacher_dashboard_context(user))
        elif user.is_platform_admin:
            context.update(stats.admin_dashboard_context(user))
        else:
            context.update(stats.default_dashboard_context(user))

        context['show_django_admin_link'] = bool(user.is_staff)
        return context
