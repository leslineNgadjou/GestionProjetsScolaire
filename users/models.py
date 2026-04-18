"""Modèle utilisateur personnalisé avec rôles métier."""

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Utilisateur de la plateforme (étudiant, enseignant ou admin métier)."""

    class Role(models.TextChoices):
        STUDENT = 'student', 'Étudiant'
        TEACHER = 'teacher', 'Enseignant'
        ADMIN = 'admin', 'Administrateur'

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.STUDENT,
        verbose_name='rôle',
    )

    class Meta:
        verbose_name = 'utilisateur'
        verbose_name_plural = 'utilisateurs'

    def __str__(self):
        return self.get_full_name() or self.username

    @property
    def is_student(self) -> bool:
        return self.role == self.Role.STUDENT

    @property
    def is_teacher(self) -> bool:
        return self.role == self.Role.TEACHER

    @property
    def is_platform_admin(self) -> bool:
        """Admin « métier » (pas confondu avec is_superuser du site admin)."""
        return self.role == self.Role.ADMIN
