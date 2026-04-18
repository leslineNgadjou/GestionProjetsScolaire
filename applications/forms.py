"""Formulaires liés aux candidatures."""

from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from projects.models import Project

from .models import Application

User = get_user_model()


class ApplicationForm(forms.ModelForm):
    """
    Dépôt ou mise à jour d’une candidature par un étudiant.

    Passer ``student=request.user`` depuis la vue. Les projets fermés ou terminés
    ne sont proposés que pour une instance déjà liée (édition d’une candidature existante).
    """

    class Meta:
        model = Application
        fields = ['project', 'motivation']
        widgets = {
            'motivation': forms.Textarea(attrs={'rows': 5}),
        }

    def __init__(self, *args, student=None, **kwargs):
        self._student = student
        super().__init__(*args, **kwargs)
        open_qs = Project.objects.filter(status=Project.Status.OPEN)
        if self.instance.pk and self.instance.project_id:
            qs = open_qs | Project.objects.filter(pk=self.instance.project_id)
        else:
            qs = open_qs
        project_field = self.fields['project']
        project_field.queryset = qs.distinct().order_by('title')
        project_field.empty_label = _('Sélectionner un projet')
        project_field.label = _('projet')

    def clean(self):
        cleaned_data = super().clean()
        student = self._student
        if student is None:
            raise ValidationError(_('Contexte étudiant manquant.'))
        if student.role != User.Role.STUDENT:
            raise ValidationError(
                _('Seuls les étudiants peuvent soumettre une candidature.'),
            )
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.student = self._student
        if commit:
            instance.save()
        return instance
