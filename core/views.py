"""Vues transverses (accueil public, pages communes)."""

from django.views.generic import TemplateView


class HomeView(TemplateView):
    """Page d'accueil publique."""

    template_name = 'core/home.html'
