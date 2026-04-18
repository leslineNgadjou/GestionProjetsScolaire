"""Formulaires utilisateur (inscription, etc.)."""

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from .models import User


class StudentRegistrationForm(UserCreationForm):
    """Création de compte étudiant : e-mail et mots de passe validés par Django."""

    email = forms.EmailField(
        required=True,
        label=_('Adresse e-mail'),
        widget=forms.EmailInput(
            attrs={
                'autocomplete': 'email',
            },
        ),
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        ctrl = 'form-control form-control-lg app-form-control'
        self.fields['username'].widget.attrs.setdefault('class', ctrl)
        self.fields['username'].widget.attrs.setdefault('autocomplete', 'username')
        self.fields['email'].widget.attrs.setdefault('class', ctrl)
        for name in ('password1', 'password2'):
            self.fields[name].widget.attrs.setdefault('class', ctrl)
            self.fields[name].widget.attrs.setdefault('autocomplete', 'new-password')

    def clean_email(self):
        email = (self.cleaned_data.get('email') or '').strip()
        if not email:
            raise ValidationError(_('Une adresse e-mail est obligatoire.'))
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError(
                _('Un compte utilise déjà cette adresse e-mail.'),
            )
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = User.Role.STUDENT
        if commit:
            user.save()
        return user
