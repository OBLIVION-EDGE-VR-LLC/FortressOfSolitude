"""Forms for the Research section."""
from django import forms
from django_ckeditor_5.widgets import CKEditor5Widget
from .models import ResearchPost


class ResearchPostForm(forms.ModelForm):
    class Meta:
        model = ResearchPost
        fields = ['title', 'slug', 'abstract', 'secure_text']
        widgets = {
            'secure_text': CKEditor5Widget(config_name='default'),
        }
