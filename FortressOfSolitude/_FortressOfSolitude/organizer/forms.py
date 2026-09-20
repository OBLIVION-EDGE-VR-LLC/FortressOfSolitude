"""
DBA 1337_TECH, AUSTIN TEXAS © created:MAY 2020 edited: July 2023
Proof of Concept code, No liabilities or warranties expressed or implied.
"""


from django import forms
from django.core.exceptions import ValidationError
from .models import NewsLink, Startup, Tag, Tasking, Librarian, UserFolder
from datetime import datetime


class MultipleFileInput(forms.FileInput):
    """FileInput subclass that allows multiple file selection."""

    def __init__(self, attrs=None):
        # Bypass parent __init__ check by going directly to Widget.__init__
        forms.Widget.__init__(self, attrs)
        if self.attrs.get('multiple') is None:
            self.attrs['multiple'] = True

    def value_from_datadict(self, data, files, name):
        return files.getlist(name)

class NewsLinkForm(forms.ModelForm):
    class Meta:
        model = NewsLink
        fields = '__all__'

class SlugCleanMixin:
    """Mixin class for slug cleaning method. """

    def clean_slug(self):
        new_slug = (self.cleaned_data['slug'].lower())
        if new_slug == 'create':
            raise ValidationError('Slug may not be "create".')
        return new_slug

class StartupForm(SlugCleanMixin, forms.ModelForm):
    class Meta:
        model = Startup
        fields = '__all__'

class TagForm(SlugCleanMixin, forms.Form):
    name = forms.CharField(max_length=32)
    slug = forms.SlugField(max_length=32, help_text='A label for URL config')

    class Meta:
        model = Tag
        fields = '__all__'

    def save(self):
        new_tag = Tag.objects.create(name=self.cleaned_data['name'],
                                     slug=self.cleaned_data['slug'])
        return new_tag

    def clean_name(self):
        return self.cleaned_data['name'].lower()

class TaskingForm(SlugCleanMixin, forms.ModelForm):

    #name = forms.CharField(max_length=32)
    #slug = forms.SlugField(max_length=32, help_text='A label for URL config')
    #asignee = forms.CharField(max_length=16, help_text='who is creating the task?')
    #project_codename = forms.CharField(max_length=32, help_text='project name (codename)')
    #description = forms.Textarea()
    #assigned_date = forms.DateTimeField(initial=datetime.now())#make into an automatically generated field and read-only

    class Meta:
        model = Tasking
        fields = '__all__'

    #def save(self):
    #    new_task = Tasking.objects.create(name=self.cleaned_data['name'],
    #                                      slug=self.cleaned_data['slug'],
    #                                      asignee=self.cleaned_data['asignee'],
    #                                      project_codename=self.cleaned_data['project_codename'],
    #                                      description=self.cleaned_data['description'],
    #                                      assigned_date=self.cleaned_data['assigned_date'])
    #    return new_task

    def clean_name(self):
        return self.cleaned_data['name'].lower()

class UploadFileForm(SlugCleanMixin, forms.Form):
    title = forms.CharField(max_length=32)
    file = forms.FileField()
    file_field = forms.FileField(widget=MultipleFileInput())
    folder = forms.ModelChoiceField(
        queryset=UserFolder.objects.none(),
        required=False,
        empty_label='(No folder)',
    )

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user is not None:
            self.fields['folder'].queryset = UserFolder.objects.filter(owner=user)
