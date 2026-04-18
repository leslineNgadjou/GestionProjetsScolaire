"""Formulaires liés aux projets."""

from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from .models import Project

User = get_user_model()


class ProjectForm(forms.ModelForm):
    """
    Création / édition d’un projet côté métier.

    Le champ « enseignant » est volontairement exclu : il sera renseigné dans
    la vue à partir de ``request.user`` (ou d’un autre flux contrôlé), ce qui
    évite qu’un étudiant choisisse un enseignant arbitrairement via POST.
    La cohérence du rôle enseignant est toutefois garantie par ``Project.clean()``.
    """

    class Meta:
        model = Project
        fields = ['title', 'description', 'domain', 'max_students', 'status']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 6}),
        }

    def clean_title(self):
        title = (self.cleaned_data.get('title') or '').strip()
        if not title:
            raise ValidationError(_('Le titre ne peut pas être vide.'))
        return title

    def save(self, commit=True, *, teacher=None):
        """
        Attache l’enseignant responsable avant enregistrement.

        ``teacher`` doit être fourni par la vue (typiquement l’utilisateur connecté).
        """
        instance = super().save(commit=False)
        if teacher is not None:
            instance.teacher = teacher
        if commit:
            instance.full_clean()
            instance.save()
        return instance
