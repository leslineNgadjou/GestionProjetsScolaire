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
    Depot ou mise a jour d'une candidature par un etudiant.

    Passer ``student=request.user`` depuis la vue. Utiliser ``fixed_project``
    pour pre-remplir un projet (champ cache) depuis la fiche projet.
    """

    class Meta:
        model = Application
        fields = ['project', 'motivation']
        widgets = {
            'motivation': forms.Textarea(
                attrs={'rows': 5, 'class': 'form-control app-form-control'},
            ),
        }

    def __init__(self, *args, student=None, fixed_project=None, **kwargs):
        self._student = student
        self._fixed_project = fixed_project
        super().__init__(*args, **kwargs)
        project_field = self.fields['project']
        if fixed_project is not None:
            project_field.widget = forms.HiddenInput()
            project_field.queryset = Project.objects.filter(pk=fixed_project.pk)
            if not self.data:
                project_field.initial = fixed_project.pk
        else:
            open_qs = Project.objects.filter(status=Project.Status.OPEN)
            if self.instance.pk and self.instance.project_id:
                qs = open_qs | Project.objects.filter(pk=self.instance.project_id)
            else:
                qs = open_qs
            project_field.queryset = qs.distinct().order_by('title')
            project_field.empty_label = _('Sélectionner un projet')
            project_field.label = _('projet')
            project_field.widget.attrs.setdefault('class', 'form-select app-form-control')

    def clean(self):
        cleaned_data = super().clean()
        student = self._student
        if student is None:
            raise ValidationError(_('Contexte étudiant manquant.'))
        if student.role != User.Role.STUDENT:
            raise ValidationError(
                _('Seuls les étudiants peuvent soumettre une candidature.'),
            )
        if self._fixed_project is not None:
            proj = cleaned_data.get('project')
            if proj and proj.pk != self._fixed_project.pk:
                raise ValidationError(_('Projet incohérent avec la page de candidature.'))
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.student = self._student
        if self._fixed_project is not None:
            instance.project = self._fixed_project
        if commit:
            instance.save()
        return instance
