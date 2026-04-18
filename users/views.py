"""Vues du module utilisateurs (inscription, etc.)."""

from django.contrib import messages
from django.contrib.auth import login
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import FormView

from .forms import StudentRegistrationForm


class RegisterView(FormView):
    """
    Inscription minimale : compte avec rôle étudiant par défaut.

    Les enseignants et admins restent créés par l'administration ou seed_demo.
    """

    template_name = 'registration/register.html'
    form_class = StudentRegistrationForm
    success_url = reverse_lazy('dashboard:index')

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('dashboard:index')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        messages.success(
            self.request,
            'Votre compte étudiant a été créé. Bienvenue sur la plateforme.',
        )
        return super().form_valid(form)
