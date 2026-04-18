"""Routage du module projects."""

from django.urls import path

from . import views

app_name = 'projects'
urlpatterns = [
    path('', views.ProjectListView.as_view(), name='list'),
    path(
        'my/export-csv/',
        views.TeacherProjectsExportCSVView.as_view(),
        name='export_csv',
    ),
    path('my/', views.MyProjectListView.as_view(), name='my_list'),
    path('create/', views.ProjectCreateView.as_view(), name='create'),
    path('<int:pk>/edit/', views.ProjectUpdateView.as_view(), name='update'),
    path('<int:pk>/delete/', views.ProjectDeleteView.as_view(), name='delete'),
    path('<int:pk>/', views.ProjectDetailView.as_view(), name='detail'),
]
