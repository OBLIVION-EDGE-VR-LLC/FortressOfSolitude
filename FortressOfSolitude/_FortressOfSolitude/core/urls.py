"""URLs for the Research section."""
from django.urls import re_path
from .views import ResearchListView, ResearchDetailView, ResearchCreateView

urlpatterns = [
    re_path(r'^$', ResearchListView.as_view(), name='research_list'),
    re_path(r'^create/$', ResearchCreateView.as_view(), name='research_create'),
    re_path(r'^(?P<pk>\d+)-(?P<slug>[\w\-]+)/$',
            ResearchDetailView.as_view(), name='research_detail'),
]
