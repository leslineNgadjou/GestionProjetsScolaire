"""Modèles liés aux candidatures étudiantes sur les projets."""

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from projects.models import Project

User = get_user_model()


class Application(models.Model):
    """Candidature d’un étudiant pour un projet donné (une seule par couple étudiant/projet)."""

    class Status(models.TextChoices):
        PENDING = 'pending', _('En attente')
        ACCEPTED = 'accepted', _('Acceptée')
        REJECTED = 'rejected', _('Refusée')

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='student_applications',
        verbose_name=_('étudiant'),
        limit_choices_to={'role': User.Role.STUDENT},
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='project_applications',
        verbose_name=_('projet'),
    )
    motivation = models.TextField(
        _('motivation'),
        validators=[MinLengthValidator(20)],
        help_text=_('Minimum 20 caractères.'),
    )
    status = models.CharField(
        _('statut'),
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    applied_at = models.DateTimeField(_('date de candidature'), auto_now_add=True)
    updated_at = models.DateTimeField(_('modifié le'), auto_now=True)

    class Meta:
        ordering = ['-applied_at']
        verbose_name = _('candidature')
        verbose_name_plural = _('candidatures')
        constraints = [
            models.UniqueConstraint(
                fields=['student', 'project'],
                name='uniq_student_application_per_project',
            ),
        ]
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['project', 'status']),
        ]

    def __str__(self) -> str:
        return f'{self.student} → {self.project}'

    def clean(self) -> None:
        super().clean()
        if self.student_id and self.student.role != User.Role.STUDENT:
            raise ValidationError(
                {
                    'student': _(
                        'Seul un utilisateur avec le rôle étudiant peut déposer '
                        'une candidature.'
                    ),
                }
            )

        if self.project_id:
            if (
                self.student_id
                and self.project.teacher_id == self.student_id
            ):
                raise ValidationError(
                    {
                        'student': _(
                            'Le responsable du projet ne peut pas être candidat '
                            'sur ce même projet.'
                        ),
                    }
                )

            # Nouvelle candidature uniquement si le projet est ouvert
            if not self.pk and self.project.status != Project.Status.OPEN:
                raise ValidationError(
                    {
                        'project': _(
                            'Ce projet n’accepte plus de nouvelles candidatures.'
                        ),
                    }
                )
