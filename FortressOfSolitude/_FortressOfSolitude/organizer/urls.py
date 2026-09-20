'''
DBA 1337_TECH, AUSTIN TEXAS © MAY 2020
Proof of Concept code, No liabilities or warranties expressed or implied.
'''

from django.conf import settings
from django.urls import re_path
from django.conf.urls.static import static
from django.contrib.auth.decorators import login_required

from .views import tag_detail, tasking_detail, TagCreate, TaskingCreate, \
    UploadFile, TaskingList, TagList, TaskingUpdate, SuccessView, DownloadImageList, \
    DownloadTheGoodsView, DownloadMusicList, DownloadTheMusicalGoodsView, DownloadMiscList, \
    DownloadTheMescalineView, FolderBrowserView, CreateSubfolderView  # , task_status

urlpatterns = [
                  re_path(r'^$',
                      login_required(TagList.as_view()),
                      name='organizer_tag_list'),
                  re_path(r'^tag/create/$',
                      login_required(TagCreate.as_view()),
                      name='organizer_tag_create'),
                  re_path(r'^tasking/create/$',
                      login_required(TaskingCreate.as_view()),
                      name='organizer_tasking_create'),
                  re_path(r'^tag/(?P<slug>[\w\-]+)/$',
                      tag_detail,
                      name='organizer_tag_detail'),
                  re_path(r'^tasking/(?P<slug>[\w\-]+)/$',
                      tasking_detail,
                      name='organizer_tasking_detail'),
                  re_path(r'^create/$',
                      login_required(TagCreate.as_view()),
                      name='organizer_tag_create'),
                  re_path(r'^upload/create/$',
                      login_required(UploadFile.as_view()),
                      name='organizer_upload_create'),
                  re_path(r'^upload/create/uploadsuccess/$',
                      login_required(SuccessView.as_view()),
                      name='organizer_upload_success'),
                  re_path(r'^tasking/$',
                      login_required(TaskingList.as_view()),
                      name='organizer_tasking_list'),
                  re_path(r'^(?P<slug>[\w\-]+)/update/$',
                      login_required(TaskingUpdate.as_view()),
                      name='organizer_tasking_update'),
                  re_path(r'^download/$',
                      login_required(DownloadImageList.as_view()),
                      name='organizer_download_pull'),
                  re_path(r'^download/music/$',
                      login_required(DownloadMusicList.as_view()),
                      name='organizer_music_download_pull'),
                  re_path(r'^download/misc/$',
                      login_required(DownloadMiscList.as_view()),
                      name='organizer_misc_download_pull'),
                  re_path(r'^download/media/photos/(?P<pk>\d+)$',
                      login_required(DownloadTheGoodsView.as_view()),
                      {'document_root': settings.MEDIA_ROOT}),
                  re_path(r'^download/music/media/music/(?P<pk>\d+)$',
                      login_required(DownloadTheMusicalGoodsView.as_view()),
                      {'document_root': settings.MEDIA_ROOT}),
                  re_path(r'^download/misc/media/otherfiles/(?P<pk>\d+)$',
                      login_required(DownloadTheMescalineView.as_view()),
                      {'document_root': settings.MEDIA_ROOT}),
                  re_path(r'^folders/$',
                      login_required(FolderBrowserView.as_view()),
                      name='organizer_folder_root'),
                  re_path(r'^folders/(?P<pk>\d+)/$',
                      login_required(FolderBrowserView.as_view()),
                      name='organizer_folder_detail'),
                  re_path(r'^folders/(?P<pk>\d+)/create/$',
                      login_required(CreateSubfolderView.as_view()),
                      name='organizer_folder_create_sub'),
                  # re_path(r'^download/(?P<path>.*)$', serve, { 'document_root': settings.STATIC_ROOT}),
                  # re_path(r'^(?P<task_id>[\w-]+)/$', task_status, name='task_status')
              ] + static('/media/', document_root=settings.MEDIA_ROOT)
