"""Serializers REST pour le modèle Project (bonus examen)."""

from rest_framework import serializers

from .models import Project


class ProjectSerializer(serializers.ModelSerializer):
    """Lecture : champs complets ; écriture : sans enseignant (déduit du compte)."""

    teacher_username = serializers.CharField(
        source='teacher.username',
        read_only=True,
    )

    class Meta:
        model = Project
        fields = [
            'id',
            'title',
            'description',
            'domain',
            'max_students',
            'status',
            'teacher',
            'teacher_username',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['teacher', 'created_at', 'updated_at']
        extra_kwargs = {
            'max_students': {
                'min_value': 1,
                'max_value': 500,
            },
        }

    def create(self, validated_data):
        request = self.context['request']
        instance = Project(teacher=request.user, **validated_data)
        instance.full_clean()
        instance.save()
        return instance
