"""Vues du module candidatures (depot, suivi etudiant, traitement enseignant)."""

import logging

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import IntegrityError, transaction
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views import View
from django.views.generic import CreateView, DetailView, ListView, RedirectView

from core.mixins import StudentRequiredMixin, TeacherRequiredMixin
from projects.models import Project

from .forms import ApplicationForm
from .models import Application

logger = logging.getLogger('applications')


class ApplicationHubView(LoginRequiredMixin, RedirectView):
    """Point d'entree /applications/ : renvoie selon le role."""

    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        user = self.request.user
        if getattr(user, 'is_student', False):
            return reverse('applications:mine')
        if getattr(user, 'is_teacher', False):
            return reverse('applications:received')
        messages.info(
            self.request,
            'Utilisez la liste des projets pour parcourir les offres.',
        )
        return reverse('projects:list')


class MyApplicationsListView(StudentRequiredMixin, ListView):
    """Candidatures de l'etudiant connecte."""

    model = Application
    template_name = 'applications/my_applications.html'
    context_object_name = 'applications'
    paginate_by = 10

    def get_queryset(self):
        return (
            Application.objects.filter(student=self.request.user)
            .select_related('project', 'project__teacher')
            .order_by('-applied_at')
        )


class ReceivedApplicationsListView(TeacherRequiredMixin, ListView):
    """Candidatures recues sur les projets de l'enseignant connecte."""

    model = Application
    template_name = 'applications/received_applications.html'
    context_object_name = 'applications'
    paginate_by = 10

    def get_queryset(self):
        return (
            Application.objects.filter(project__teacher=self.request.user)
            .select_related('project', 'student')
            .order_by('-applied_at')
        )


class ApplicationCreateView(StudentRequiredMixin, CreateView):
    """Depot d'une candidature sur un projet ouvert."""

    model = Application
    form_class = ApplicationForm
    template_name = 'applications/application_form.html'

    def dispatch(self, request, *args, **kwargs):
        self.project = get_object_or_404(
            Project.objects.filter(status=Project.Status.OPEN),
            pk=kwargs['project_id'],
        )
        if request.user.is_authenticated and Application.objects.filter(
            student=request.user,
            project=self.project,
        ).exists():
            messages.warning(
                request,
                'Vous avez déjà postulé pour ce projet.',
            )
            return redirect('projects:detail', pk=self.project.pk)
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['student'] = self.request.user
        kwargs['fixed_project'] = self.project
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['project'] = self.project
        context['form_title'] = 'Postuler au projet'
        return context

    def form_valid(self, form):
        try:
            self.object = form.save()
        except IntegrityError:
            logger.warning(
                'Candidature en double refusee (integrite): projet=%s etudiant=%s',
                self.project.pk,
                self.request.user.pk,
            )
            messages.error(
                self.request,
                'Une candidature existe déjà pour ce projet.',
            )
            return redirect('projects:detail', pk=self.project.pk)
        messages.success(
            self.request,
            'Votre candidature a bien été envoyée.',
        )
        logger.info(
            '[Notification simulee] Nouvelle candidature id=%s projet=%s etudiant=%s',
            self.object.pk,
            self.project.pk,
            self.request.user.username,
        )
        return HttpResponseRedirect(self.object.get_absolute_url())

    def form_invalid(self, form):
        messages.error(
            self.request,
            'Veuillez corriger les erreurs du formulaire.',
        )
        return super().form_invalid(form)


class ApplicationDetailView(LoginRequiredMixin, DetailView):
    """
    Détail candidature :

    - étudiant : uniquement ses dossiers ;
    - enseignant : candidatures sur ses projets ;
    - administrateur métier : tous les dossiers en lecture seule (pas d'action accepter/refuser).
    """

    model = Application
    template_name = 'applications/application_detail.html'
    context_object_name = 'application'

    def get_queryset(self):
        user = self.request.user
        qs = Application.objects.select_related(
            'project',
            'student',
            'project__teacher',
        )
        if getattr(user, 'is_platform_admin', False):
            return qs
        if getattr(user, 'is_student', False):
            return qs.filter(student=user)
        if getattr(user, 'is_teacher', False):
            return qs.filter(project__teacher=user)
        return qs.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        application = self.object
        project = application.project
        context['can_teacher_act'] = (
            getattr(self.request.user, 'is_teacher', False)
            and project.teacher_id == self.request.user.id
            and application.status == Application.Status.PENDING
        )
        context['project_capacity_reached'] = not project.can_accept_more_students()
        return context


class AcceptApplicationView(TeacherRequiredMixin, View):
    """Accepte une candidature en attente (POST uniquement)."""

    http_method_names = ['post', 'options']

    def post(self, request, pk):
        application = get_object_or_404(
            Application.objects.select_related('project'),
            pk=pk,
            project__teacher=request.user,
        )
        if application.status != Application.Status.PENDING:
            messages.warning(
                request,
                'Cette candidature a déjà été traitée.',
            )
            return redirect('applications:detail', pk=application.pk)

        with transaction.atomic():
            project = Project.objects.select_for_update().get(pk=application.project_id)
            accepted = project.project_applications.filter(
                status=Application.Status.ACCEPTED,
            ).count()
            if accepted >= project.max_students:
                messages.error(
                    request,
                    'Le nombre maximal d’étudiants acceptés est atteint pour ce projet.',
                )
                logger.info(
                    '[Notification simulee] Acceptation refusee (plein): '
                    'candidature=%s projet=%s',
                    application.pk,
                    project.pk,
                )
                return redirect('applications:detail', pk=application.pk)
            application.status = Application.Status.ACCEPTED
            application.save()

        messages.success(
            request,
            'La candidature a été acceptée.',
        )
        logger.info(
            '[Notification simulee] Candidature acceptee id=%s projet=%s etudiant=%s',
            application.pk,
            project.pk,
            application.student.username,
        )
        return redirect('applications:detail', pk=application.pk)


class RejectApplicationView(TeacherRequiredMixin, View):
    """Refuse une candidature en attente (POST uniquement)."""

    http_method_names = ['post', 'options']

    def post(self, request, pk):
        application = get_object_or_404(
            Application.objects.select_related('project', 'student'),
            pk=pk,
            project__teacher=request.user,
        )
        if application.status != Application.Status.PENDING:
            messages.warning(
                request,
                'Cette candidature a déjà été traitée.',
            )
            return redirect('applications:detail', pk=application.pk)

        application.status = Application.Status.REJECTED
        application.save()
        messages.success(
            request,
            'La candidature a été refusée.',
        )
        logger.info(
            '[Notification simulee] Candidature refusee id=%s projet=%s etudiant=%s',
            application.pk,
            application.project_id,
            application.student.username,
        )
        return redirect('applications:detail', pk=application.pk)
