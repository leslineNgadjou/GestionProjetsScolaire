"""Administration Django pour les candidatures."""

from django.contrib import admin

from .models import Application


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = (
        'student',
        'project',
        'status',
        'applied_at',
        'updated_at',
    )
    list_filter = ('status', 'applied_at', 'project__domain')
    search_fields = (
        'motivation',
        'student__username',
        'student__first_name',
        'student__last_name',
        'student__email',
        'project__title',
    )
    ordering = ('-applied_at',)
    date_hierarchy = 'applied_at'
    readonly_fields = ('applied_at', 'updated_at')
    autocomplete_fields = ('student', 'project')
    fieldsets = (
        (None, {'fields': ('student', 'project', 'motivation', 'status')}),
        ('Horodatage', {'fields': ('applied_at', 'updated_at')}),
    )
