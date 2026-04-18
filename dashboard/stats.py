"""Agregations ORM pour le tableau de bord (par role)."""

from django.db.models import Count, Q

from applications.models import Application
from projects.models import Project
from users.models import User


def student_dashboard_context(user):
    """Statistiques et listes pour un compte etudiant."""
    applications = Application.objects.filter(student=user)
    stats = applications.aggregate(
        total=Count('pk'),
        pending=Count('pk', filter=Q(status=Application.Status.PENDING)),
        accepted=Count('pk', filter=Q(status=Application.Status.ACCEPTED)),
        rejected=Count('pk', filter=Q(status=Application.Status.REJECTED)),
    )
    recent_applications = list(
        applications.select_related('project', 'project__teacher').order_by(
            '-applied_at',
        )[:5],
    )
    return {
        'dashboard_role': 'student',
        'dashboard_title': 'Tableau de bord étudiant',
        'dashboard_subtitle': 'Vue d’ensemble de vos candidatures aux projets.',
        'stats': stats,
        'recent_applications': recent_applications,
    }


def teacher_dashboard_context(user):
    """Statistiques pour un compte enseignant (projets + candidatures recues)."""
    projects = Project.objects.filter(teacher=user)
    project_stats = projects.aggregate(
        total=Count('pk'),
        open_count=Count('pk', filter=Q(status=Project.Status.OPEN)),
        closed_count=Count('pk', filter=Q(status=Project.Status.CLOSED)),
        completed_count=Count('pk', filter=Q(status=Project.Status.COMPLETED)),
    )
    received = Application.objects.filter(project__teacher=user)
    application_stats = received.aggregate(
        total=Count('pk'),
        pending=Count('pk', filter=Q(status=Application.Status.PENDING)),
        accepted=Count('pk', filter=Q(status=Application.Status.ACCEPTED)),
        rejected=Count('pk', filter=Q(status=Application.Status.REJECTED)),
    )
    recent_projects = list(
        projects.select_related('teacher').order_by('-created_at')[:5],
    )
    recent_applications = list(
        received.select_related('project', 'student').order_by('-applied_at')[:5],
    )
    return {
        'dashboard_role': 'teacher',
        'dashboard_title': 'Tableau de bord enseignant',
        'dashboard_subtitle': 'Vos projets et les candidatures associées.',
        'project_stats': project_stats,
        'application_stats': application_stats,
        'recent_projects': recent_projects,
        'recent_applications': recent_applications,
    }


def admin_dashboard_context(_user):
    """Statistiques globales pour un administrateur metier (role admin)."""
    user_stats = User.objects.aggregate(
        total=Count('pk'),
        students=Count('pk', filter=Q(role=User.Role.STUDENT)),
        teachers=Count('pk', filter=Q(role=User.Role.TEACHER)),
        admins=Count('pk', filter=Q(role=User.Role.ADMIN)),
    )
    project_stats = Project.objects.aggregate(
        total=Count('pk'),
        open_count=Count('pk', filter=Q(status=Project.Status.OPEN)),
        closed_count=Count('pk', filter=Q(status=Project.Status.CLOSED)),
        completed_count=Count('pk', filter=Q(status=Project.Status.COMPLETED)),
    )
    application_stats = Application.objects.aggregate(
        total=Count('pk'),
        pending=Count('pk', filter=Q(status=Application.Status.PENDING)),
        accepted=Count('pk', filter=Q(status=Application.Status.ACCEPTED)),
        rejected=Count('pk', filter=Q(status=Application.Status.REJECTED)),
    )
    admin_chart_users = {
        'labels': ['Étudiants', 'Enseignants', 'Administrateurs'],
        'values': [
            user_stats['students'],
            user_stats['teachers'],
            user_stats['admins'],
        ],
    }
    admin_chart_applications = {
        'labels': ['En attente', 'Acceptées', 'Refusées'],
        'values': [
            application_stats['pending'],
            application_stats['accepted'],
            application_stats['rejected'],
        ],
    }
    admin_chart_projects = {
        'labels': ['Ouverts', 'Fermés', 'Terminés'],
        'values': [
            project_stats['open_count'],
            project_stats['closed_count'],
            project_stats['completed_count'],
        ],
    }
    return {
        'dashboard_role': 'admin',
        'dashboard_title': 'Tableau de bord administrateur',
        'dashboard_subtitle': 'Indicateurs globaux de la plateforme.',
        'user_stats': user_stats,
        'project_stats': project_stats,
        'application_stats': application_stats,
        'admin_chart_users': admin_chart_users,
        'admin_chart_applications': admin_chart_applications,
        'admin_chart_projects': admin_chart_projects,
    }


def default_dashboard_context(user):
    """Contexte minimal si le role n’est pas reconnu (ne devrait pas arriver)."""
    return {
        'dashboard_role': 'default',
        'dashboard_title': 'Tableau de bord',
        'dashboard_subtitle': f'Bienvenue, {user.get_username()}.',
        'stats': {'total': 0, 'pending': 0, 'accepted': 0, 'rejected': 0},
        'recent_applications': [],
    }
