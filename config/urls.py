"""
Routage principal : inclut les urls des apps et l'admin.
"""

from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path(
        'accounts/login/',
        auth_views.LoginView.as_view(template_name='registration/login.html'),
        name='login',
    ),
    path(
        'accounts/logout/',
        auth_views.LogoutView.as_view(),
        name='logout',
    ),
    path('projects/', include('projects.urls')),
    path('applications/', include('applications.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('', include('core.urls')),
]
