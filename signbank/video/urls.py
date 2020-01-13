# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.urls import path
# Views
from . import views

urlpatterns = [
    path('<intvideoid>/', views.video_view, name='glossvideo'),
    path('poster/<int:videoid>', views.poster_view, name='glossvideo_poster'),
    path('upload/', views.upload_glossvideo_view, name='upload_glossvideo'),
    path('upload/gloss/', views.upload_glossvideo_gloss_view, name='upload_glossvideo_gloss'),
    path('upload/recorded/', views.add_recorded_video_view, name='add_recorded_video'),
    # View to upload multiple videos with no foreign key to gloss.
    path('add/', views.addvideos_formview, name='upload_videos'),
    # View that shows a list of glossvideos with no foreign key to gloss, user can add fk to gloss for glossvideos.
    path('uploaded/', views.uploaded_glossvideos_listview, name='manage_videos'),
    # View that updates a glossvideo
    path('update/', views.update_glossvideo_view, name='glossvideo_update'),
    # View that handles the upload of poster file
    path('add/poster', views.add_poster_view, name='add_poster'),
    # Change priority of video
    path('order/', views.change_glossvideo_order, name='change_glossvideo_order'),
    # Change publicity of video
    path('publicity/', views.change_glossvideo_publicity, name='change_glossvideo_publicity'),
]
