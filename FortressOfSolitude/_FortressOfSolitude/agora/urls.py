"""
DBA 1337_TECH, AUSTIN TEXAS
Proof of Concept code, No liabilities or warranties expressed or implied.
"""

from django.urls import re_path

from .views import (
    AgoraLandingView,
    AgoraProfileSetupView,
    AgoraProfileEditView,
    AgoraProfileDetailView,
    CategoryDetailView,
    TopicCreateView,
    TopicDetailView,
    ReplyCreateView,
)

urlpatterns = [
    re_path(r'^$',
        AgoraLandingView.as_view(),
        name='agora_landing'),
    re_path(r'^setup/$',
        AgoraProfileSetupView.as_view(),
        name='agora_profile_setup'),
    re_path(r'^profile/edit/$',
        AgoraProfileEditView.as_view(),
        name='agora_profile_edit'),
    re_path(r'^profile/(?P<handle>[\w-]+)/$',
        AgoraProfileDetailView.as_view(),
        name='agora_profile_detail'),
    re_path(r'^(?P<category_slug>[\w-]+)/$',
        CategoryDetailView.as_view(),
        name='agora_category_detail'),
    re_path(r'^(?P<category_slug>[\w-]+)/new/$',
        TopicCreateView.as_view(),
        name='agora_topic_create'),
    re_path(r'^(?P<category_slug>[\w-]+)/(?P<pk>\d+)-(?P<slug>[\w-]+)/$',
        TopicDetailView.as_view(),
        name='agora_topic_detail'),
    re_path(r'^(?P<category_slug>[\w-]+)/(?P<pk>\d+)-(?P<slug>[\w-]+)/reply/$',
        ReplyCreateView.as_view(),
        name='agora_reply_create'),
]
