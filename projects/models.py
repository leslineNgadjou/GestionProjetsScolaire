"""Modèles liés aux projets publiés par les enseignants."""

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class Project(models.Model):
    """Projet universitaire publié par un enseignant."""

    class Status(models.TextChoices):
        OPEN = 'open', _('Ouvert aux candidatures')
        CLOSED = 'closed', _('Fermé')
        COMPLETED = 'completed', _('Terminé')

    title = models.CharField(_('titre'), max_length=200)
    description = models.TextField(_('description'))
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='teaching_projects',
        verbose_name=_('enseignant'),
        limit_choices_to={'role': User.Role.TEACHER},
    )
    domain = models.CharField(_('domaine'), max_length=120)
    max_students = models.PositiveIntegerField(
        _('nombre maximal d’étudiants'),
        validators=[
            MinValueValidator(1),
            MaxValueValidator(500),
        ],
        help_text=_('Entre 1 et 500.'),
    )
    status = models.CharField(
        _('statut'),
        max_length=20,
        choices=Status.choices,
        default=Status.OPEN,
    )
    created_at = models.DateTimeField(_('créé le'), auto_now_add=True)
    updated_at = models.DateTimeField(_('modifié le'), auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = _('projet')
        verbose_name_plural = _('projets')
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['teacher', '-created_at']),
        ]

    def __str__(self) -> str:
        return self.title

    def get_absolute_url(self):
        from django.urls import reverse

        return reverse('projects:detail', kwargs={'pk': self.pk})

    @property
    def is_accepting_applications(self) -> bool:
        """Indique si de nouvelles candidatures étudiantes sont permises."""
        return self.status == self.Status.OPEN

    def accepted_applications_count(self) -> int:
        """Nombre de candidatures acceptees sur ce projet."""
        return self.project_applications.filter(
            status='accepted',
        ).count()

    def can_accept_more_students(self) -> bool:
        """True si une nouvelle candidature peut encore etre acceptee (places restantes)."""
        return self.accepted_applications_count() < self.max_students

    def clean(self) -> None:
        super().clean()
        title = (self.title or '').strip()
        if not title:
            raise ValidationError({'title': _('Le titre ne peut pas être vide.')})
        self.title = title

        if self.teacher_id:
            if self.teacher.role != User.Role.TEACHER:
                raise ValidationError(
                    {
                        'teacher': _(
                            'Seul un utilisateur avec le rôle enseignant peut être '
                            'responsable d’un projet.'
                        ),
                    }
                )
