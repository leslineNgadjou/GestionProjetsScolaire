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

    _max_field = Project._meta.get_field('max_students')

    max_students = forms.IntegerField(
        min_value=1,
        max_value=500,
        label=_max_field.verbose_name,
        help_text=_max_field.help_text,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control app-form-control',
                'inputmode': 'numeric',
                'autocomplete': 'off',
                'maxlength': '3',
                'placeholder': '1 – 500',
                'data-app-digits-only': '1',
                'data-app-int-min': '1',
                'data-app-int-max': '500',
            },
        ),
    )

    class Meta:
        model = Project
        fields = ['title', 'description', 'domain', 'max_students', 'status']
        widgets = {
            'title': forms.TextInput(
                attrs={'class': 'form-control app-form-control'},
            ),
            'description': forms.Textarea(
                attrs={'rows': 6, 'class': 'form-control app-form-control'},
            ),
            'domain': forms.TextInput(
                attrs={'class': 'form-control app-form-control'},
            ),
            'status': forms.Select(attrs={'class': 'form-select app-form-control'}),
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
