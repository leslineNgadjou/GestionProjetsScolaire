"""Routage projet — à compléter (liste, détail, CRUD enseignant, etc.)."""

from django.urls import path

from . import views

app_name = 'projects'
urlpatterns = [
    path('', views.index, name='index'),
]
