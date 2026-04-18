"""Routage API REST sous le préfixe /api/."""

from django.urls import path

from . import api_views

app_name = 'projects_api'

urlpatterns = [
    path(
        'projects/',
        api_views.ProjectListCreateAPIView.as_view(),
        name='project-list',
    ),
    path(
        'projects/<int:pk>/',
        api_views.ProjectDetailAPIView.as_view(),
        name='project-detail',
    ),
]
