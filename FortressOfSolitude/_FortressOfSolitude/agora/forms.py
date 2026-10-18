"""
DBA 1337_TECH, AUSTIN TEXAS
Proof of Concept code, No liabilities or warranties expressed or implied.
"""

from django import forms
from django_ckeditor_5.widgets import CKEditor5Widget

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
        widgets = {
            'secure_text': CKEditor5Widget(config_name='default'),
        }


class ReplyForm(forms.Form):
    secure_text = forms.CharField(
        widget=CKEditor5Widget(config_name='default'),
        label='',
    )
