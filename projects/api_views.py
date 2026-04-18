"""Vues API REST minimales sur les projets (bonus examen)."""

from django.db.models import Q
from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated

from .models import Project
from .permissions import IsTeacherUser
from .serializers import ProjectSerializer


class ProjectListCreateAPIView(generics.ListCreateAPIView):
    """
    GET : liste paginée (10 / page) — projets ouverts pour le public ;
    enseignant connecté voit aussi ses propres projets (tous statuts).
    POST : création réservée aux enseignants authentifiés.
    """

    serializer_class = ProjectSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsTeacherUser()]
        return [AllowAny()]

    def get_queryset(self):
        qs = Project.objects.select_related('teacher').order_by('-created_at')
        user = self.request.user
        if not user.is_authenticated:
            return qs.filter(status=Project.Status.OPEN)
        if getattr(user, 'is_teacher', False):
            return qs.filter(
                Q(status=Project.Status.OPEN) | Q(teacher=user),
            )
        return qs.filter(status=Project.Status.OPEN)


class ProjectDetailAPIView(generics.RetrieveAPIView):
    """
    GET : détail si projet ouvert, ou si enseignant propriétaire (tout statut).
    """

    serializer_class = ProjectSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        qs = Project.objects.select_related('teacher')
        user = self.request.user
        if not user.is_authenticated:
            return qs.filter(status=Project.Status.OPEN)
        if getattr(user, 'is_teacher', False):
            return qs.filter(
                Q(status=Project.Status.OPEN) | Q(teacher=user),
            )
        return qs.filter(status=Project.Status.OPEN)
