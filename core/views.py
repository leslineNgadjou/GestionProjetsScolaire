"""Vues transverses (accueil public, pages communes)."""

from django.shortcuts import render
from django.views.generic import TemplateView


class HomeView(TemplateView):
    """Page d'accueil publique."""

    template_name = 'core/home.html'


def error_404(request, exception):
    """Page 404 personnalisée (utilisée lorsque DEBUG=False)."""

    return render(request, 'errors/404.html', status=404)


def error_403(request, exception=None):
    """Page 403 personnalisée."""

    context = {}
    if exception is not None:
        args = getattr(exception, 'args', ())
        if args and args[0]:
            context['exception_message'] = str(args[0])
    return render(request, 'errors/403.html', context, status=403)


def error_500(request):
    """Page 500 personnalisée (utilisée lorsque DEBUG=False)."""

    return render(request, 'errors/500.html', status=500)
