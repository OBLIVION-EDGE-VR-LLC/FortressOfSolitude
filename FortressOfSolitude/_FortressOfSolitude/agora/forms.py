"""
DBA 1337_TECH, AUSTIN TEXAS
Proof of Concept code, No liabilities or warranties expressed or implied.
"""

from django import forms

from .models import AgoraProfile, Topic


class AgoraProfileForm(forms.ModelForm):
    class Meta:
        model = AgoraProfile
        fields = ['handle', 'about_me', 'favorite_movie', 'favorite_song',
                  'favorite_artist', 'quote']


class TopicForm(forms.ModelForm):
    class Meta:
        model = Topic
        fields = ['title', 'slug', 'secure_text']
