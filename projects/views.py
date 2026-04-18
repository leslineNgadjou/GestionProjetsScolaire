"""Vues du module gestion des projets (liste publique, detail, CRUD enseignant)."""

import csv

from django.contrib import messages
from django.http import HttpResponse
from django.db.models import Q
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import DeleteView, DetailView, ListView
from django.views.generic.edit import CreateView, UpdateView

from applications.models import Application

from core.mixins import TeacherRequiredMixin

from .forms import ProjectForm
from .mixins import TeacherOwnedProjectsMixin
from .models import Project


class ProjectListView(ListView):
    """Liste publique des projets ouverts, avec recherche, filtre domaine et pagination."""

    model = Project
    template_name = 'projects/project_list.html'
    context_object_name = 'project_list'
    paginate_by = 10

    def get_queryset(self):
        qs = (
            Project.objects.filter(status=Project.Status.OPEN)
            .select_related('teacher')
            .order_by('-created_at')
        )
        q = self.request.GET.get('q', '').strip()
        if q:
            qs = qs.filter(title__icontains=q)
        domain = self.request.GET.get('domain', '').strip()
        if domain:
            qs = qs.filter(domain__iexact=domain)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['domain_choices'] = (
            Project.objects.filter(status=Project.Status.OPEN)
            .values_list('domain', flat=True)
            .distinct()
            .order_by('domain')
        )
        context['current_q'] = self.request.GET.get('q', '')
        context['current_domain'] = self.request.GET.get('domain', '')
        return context


class ProjectDetailView(DetailView):
    """Fiche projet : projets ouverts pour tous ; projets fermes visibles par leur enseignant."""

    model = Project
    template_name = 'projects/project_detail.html'
    context_object_name = 'project'

    def get_queryset(self):
        base = Project.objects.select_related('teacher')
        user = self.request.user
        if not user.is_authenticated:
            return base.filter(status=Project.Status.OPEN)
        if getattr(user, 'is_teacher', False):
            return base.filter(
                Q(status=Project.Status.OPEN) | Q(teacher=user),
            )
        return base.filter(status=Project.Status.OPEN)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project = self.object
        user = self.request.user
        context['student_application'] = None
        if user.is_authenticated and getattr(user, 'is_student', False):
            context['student_application'] = (
                Application.objects.filter(student=user, project=project).first()
            )
        context['accepted_count'] = project.accepted_applications_count()
        context['slots_remaining'] = max(
            0,
            project.max_students - context['accepted_count'],
        )
        return context


class MyProjectListView(TeacherRequiredMixin, ListView):
    """Projets dont l'enseignant connecte est responsable (tous statuts)."""

    model = Project
    template_name = 'projects/my_project_list.html'
    context_object_name = 'project_list'
    paginate_by = 10

    def get_queryset(self):
        return (
            Project.objects.filter(teacher=self.request.user)
            .select_related('teacher')
            .order_by('-created_at')
        )


class ProjectCreateView(TeacherRequiredMixin, CreateView):
    """Creation d'un projet par l'enseignant connecte."""

    model = Project
    form_class = ProjectForm
    template_name = 'projects/project_form.html'
    extra_context = {'form_title': 'Nouveau projet'}

    def form_valid(self, form):
        project = form.save(commit=True, teacher=self.request.user)
        messages.success(
            self.request,
            'Le projet a été créé avec succès.',
        )
        return redirect(project.get_absolute_url())

    def form_invalid(self, form):
        messages.error(
            self.request,
            'Veuillez corriger les erreurs du formulaire.',
        )
        return super().form_invalid(form)


class ProjectUpdateView(TeacherOwnedProjectsMixin, UpdateView):
    """Mise a jour d'un projet appartenant a l'enseignant connecte."""

    model = Project
    form_class = ProjectForm
    template_name = 'projects/project_form.html'
    extra_context = {'form_title': 'Modifier le projet'}

    def form_valid(self, form):
        project = form.save(commit=True, teacher=self.request.user)
        messages.success(
            self.request,
            'Le projet a été mis à jour avec succès.',
        )
        return redirect(project.get_absolute_url())

    def form_invalid(self, form):
        messages.error(
            self.request,
            'Veuillez corriger les erreurs du formulaire.',
        )
        return super().form_invalid(form)


class ProjectDeleteView(TeacherOwnedProjectsMixin, DeleteView):
    """Suppression d'un projet appartenant a l'enseignant connecte."""

    model = Project
    template_name = 'projects/project_confirm_delete.html'
    success_url = reverse_lazy('projects:my_list')
    context_object_name = 'project'

    def delete(self, request, *args, **kwargs):
        messages.success(
            request,
            'Le projet a été supprimé avec succès.',
        )
        return super().delete(request, *args, **kwargs)


class TeacherProjectsExportCSVView(TeacherRequiredMixin, View):
    """
    Export CSV des projets du enseignant connecte (bonus examen).

    Colonnes : id, title, domain, status, max_students, created_at
    """

    http_method_names = ['get', 'head', 'options']

    def get(self, request, *args, **kwargs):
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = (
            'attachment; filename="mes_projets_export.csv"'
        )
        writer = csv.writer(response)
        writer.writerow(
            ['id', 'title', 'domain', 'status', 'max_students', 'created_at'],
        )
        for project in (
            Project.objects.filter(teacher=request.user)
            .order_by('-created_at')
            .iterator()
        ):
            writer.writerow(
                [
                    project.pk,
                    project.title,
                    project.domain,
                    project.status,
                    project.max_students,
                    project.created_at.isoformat(),
                ],
            )
        return response
