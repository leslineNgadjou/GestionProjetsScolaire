"""Administration Django pour les projets."""

from django.contrib import admin

from .models import Project


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'teacher',
        'domain',
        'status',
        'max_students',
        'created_at',
    )
    list_filter = ('status', 'domain', 'created_at')
    search_fields = (
        'title',
        'description',
        'domain',
        'teacher__username',
        'teacher__first_name',
        'teacher__last_name',
        'teacher__email',
    )
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at', 'updated_at')
    autocomplete_fields = ('teacher',)
    fieldsets = (
        (None, {'fields': ('title', 'description', 'domain', 'teacher')}),
        (
            'Paramètres',
            {'fields': ('max_students', 'status')},
        ),
        (
            'Horodatage',
            {'fields': ('created_at', 'updated_at')},
        ),
    )
