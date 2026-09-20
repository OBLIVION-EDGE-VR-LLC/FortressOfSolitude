"""
DBA 1337_TECH, AUSTIN TEXAS © MAY 2021
Proof of Concept code, No liabilities or warranties expressed or implied.
"""

from django.urls import re_path

from .views import (PostCreate,
                    PostDelete, PostDetail, PostList, PostUpdate, PostArchiveYear, PostArchiveMonth, SecurePostList,
                    SecurePostDetail,
                    SecurePostCreate, SecurePostUpdate, SecurePostDelete, SecurePostArchiveYear,
                    SecurePostArchiveMonth, PublicSecurePostCreate, PublicSecurePostDelete, PublicSecurePostDetail,
                    PublicSecurePostUpdate, PublicSecurePostList, PublicSecurePostArchiveYear,
                    PublicSecurePostArchiveMonth)

urlpatterns = [
    re_path(r'^Securelist/$',
        SecurePostList.as_view(),
        name='blog_securepost_list'),
    re_path(r'^$',
        PostList.as_view(),
        name='blog_post_list'),
    re_path(r'^Securecreate/$',
        SecurePostCreate.as_view(),
        name='blog_securepost_create'),
    re_path(r'^create/$',
        PostCreate.as_view(),
        name='blog_post_create'),
    re_path(r'^(?P<year>\d{4})/$',
        PostArchiveYear.as_view(),
        name='blog_post_archive_year'),
    re_path(r'^(?P<year>\d{4})/'
        r'(?P<month>\d{1,2})/$',
        PostArchiveMonth.as_view(),
        name='blog_post_archive_month'),
    re_path(r'^SecureNote/(?P<year>\d{4})/'
        r'(?P<month>\d{1,2})/'
        r'(?P<slug>[\w\-]+)/$',
        SecurePostDetail.as_view(),
        name='blog_securepost_detail'),
    re_path(r'^SecureNote/(?P<year>\d{4})/'
        r'(?P<month>\d{1,2})/'
        r'(?P<slug>[\w\-]+)/$',
        SecurePostUpdate.as_view(),
        name='blog_secureNote_form_update'),
    re_path(r'^SecureNote/'
        r'(?P<year>\d{4})/'
        r'(?P<month>\d{1,2})/'
        r'(?P<slug>[\w\-]+)/'
        r'delete/$',
        SecurePostDelete.as_view(),
        name='blog_secureNote_delete'),

    # Public Viewable Blog
    re_path(r'^PublicSecurelist/$',
        PublicSecurePostList.as_view(),
        name='blog_securepost_public_list'),
    re_path(r'^PublicSecurecreate/$',
        PublicSecurePostCreate.as_view(),
        name='blog_securepost_public_create'),
    re_path(r'^PublicSecureNote/(?P<year>\d{4})/'
        r'(?P<month>\d{1,2})/'
        r'(?P<slug>[\w\-]+)/$',
        PublicSecurePostDetail.as_view(),
        name='blog_securepost_public_detail'),
    re_path(r'^PublicSecureNote/'
        r'(?P<year>\d{4})/$',
        PublicSecurePostArchiveYear.as_view(),
        name='blog_securepost_public_archive_year'),
    re_path(r'^PublicSecureNote/(?P<year>\d{4})/'
        r'(?P<month>\d{1,2})/$',
        PublicSecurePostArchiveMonth.as_view(),
        name='blog_securepost_public_archive_month'),
    re_path(r'PublicSecureNoteUpdate/(?P<year>\d{4})/'
        r'(?P<month>\d{1,2})/'
        r'(?P<slug>[\w\-]+)/$',
        PublicSecurePostUpdate.as_view(),
        name='blog_securepost_public_update'),
    re_path(r'^PublicSecureNote/'
        r'(?P<year>\d{4})/'
        r'(?P<month>\d{1,2})/'
        r'(?P<slug>[\w\-]+)/'
        r'delete/$',
        PublicSecurePostDelete.as_view(),
        name='blog_securepost_public_delete'),
    # END of Public Viewable Posts

    re_path(r'^(?P<year>\d{4})/'
        r'(?P<month>\d{1,2})/'
        r'(?P<slug>[\w\-]+)/$',
        PostDetail.as_view(),
        name='blog_post_detail'),
    re_path(r'^(?P<year>\d{4})/'
        r'(?P<month>\d{1,2})/'
        r'(?P<slug>[\w\-]+)/'
        r'delete/$',
        PostDelete.as_view(),
        name='blog_post_delete'),
    re_path(r'^(?P<year>\d{4})/'
        r'(?P<month>\d{1,2})/'
        r'(?P<slug>[\w\-]+)/'
        r'Secureupdate/$',
        SecurePostUpdate.as_view(),
        name='blog_securepost_update'),
    re_path(r'^(?P<year>\d{4})/'
        r'(?P<month>\d{1,2})/'
        r'(?P<slug>[\w\-]+)/'
        r'update/$',
        PostUpdate.as_view(),
        name='blog_post_update'),
    re_path(r'^SecureNote/'
        r'(?P<year>\d{4})/$',
        SecurePostArchiveYear.as_view(),
        name='blog_securepost_archive_year'),
    re_path(r'^SecureNote/(?P<year>\d{4})/'
        r'(?P<month>\d{1,2})/$',
        SecurePostArchiveMonth.as_view(),
        name='blog_securepost_archive_month'),
]
