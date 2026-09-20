"""
DBA 1337_TECH, AUSTIN TEXAS © MAY 2022
Proof of Concept code, No liabilities or warranties expressed or implied.
"""

from django import forms
from django.contrib.auth import password_validation
from django.contrib.auth.forms import UsernameField, UserCreationForm
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from .models import User
from _FortressOfSolitude.NeutrinoKey.models import UserKeyPair
from _FortressOfSolitude.organizer.models import UserFolder


class DailyPlanetSubscriber(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=False, help_text='Optional')
    last_name = forms.CharField(max_length=30, required=False, help_text='Optional')
    email = forms.EmailField(max_length=254, help_text='Enter a valid email address')

    class Meta:
        model = User
        fields = [
            'first_name',
            'last_name',
            'email',
            'password1',
            'password2',
            ]

    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            raw_password = self.cleaned_data['password1']
            password_bytes = raw_password.encode()
            # Generate RSA-4096 key pair for the new user, encrypted with their password
            UserKeyPair.generate_for_user(user, password_bytes)
            # Create encrypted folder hierarchy for the new user
            UserFolder.create_root_for_user(user, password_bytes)
        return user
