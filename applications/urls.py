"""Routage du module candidatures."""

from django.urls import path

from . import views

app_name = 'applications'
urlpatterns = [
    path('', views.ApplicationHubView.as_view(), name='index'),
    path('mine/', views.MyApplicationsListView.as_view(), name='mine'),
    path('received/', views.ReceivedApplicationsListView.as_view(), name='received'),
    path(
        'create/<int:project_id>/',
        views.ApplicationCreateView.as_view(),
        name='create',
    ),
    path('<int:pk>/accept/', views.AcceptApplicationView.as_view(), name='accept'),
    path('<int:pk>/reject/', views.RejectApplicationView.as_view(), name='reject'),
    path('<int:pk>/', views.ApplicationDetailView.as_view(), name='detail'),
]
