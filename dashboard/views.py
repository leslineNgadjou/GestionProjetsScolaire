"""Vues du tableau de bord (seront enrichies par rôle plus tard)."""

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView


class DashboardIndexView(LoginRequiredMixin, TemplateView):
    """Espace connecté : squelette avant logique par rôle."""

    template_name = 'dashboard/index.html'
