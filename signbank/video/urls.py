# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import url
# Views
from . import views

urlpatterns = [
    url(r'^(?P<videoid>\d+)/$', views.video_view, name='glossvideo'),
    url(r'^poster/(?P<videoid>\d+)$', views.poster_view, name='glossvideo_poster'),
    url(r'^upload/$', views.upload_glossvideo_view, name='upload_glossvideo'),
    url(r'^upload/gloss/$', views.upload_glossvideo_gloss_view, name='upload_glossvideo_gloss'),
    url(r'^upload/recorded/$', views.add_recorded_video_view, name='add_recorded_video'),
    # View to upload multiple videos with no foreign key to gloss.
    url(r'^add/$', views.addvideos_formview, name='upload_videos'),
    # View that shows a list of glossvideos with no foreign key to gloss, user can add fk to gloss for glossvideos.
    url(r'^uploaded/$', views.uploaded_glossvideos_listview, name='manage_videos'),
    # View that updates a glossvideo
    url(r'^update/$', views.update_glossvideo_view, name='glossvideo_update'),
    # View that handles the upload of poster file
    url(r'^add/poster$', views.add_poster_view, name='add_poster'),
    # Change priority of video
    url(r'^order/$', views.change_glossvideo_order, name='change_glossvideo_order'),
    # Change publicity of video
    url(r'^publicity/$', views.change_glossvideo_publicity, name='change_glossvideo_publicity'),
]
