from django.conf.urls import url
from django.contrib.auth.decorators import permission_required
# Views
from . import views

urlpatterns = [
    url(r'^(?P<videoid>\d+)$', views.video_view),
    url(r'^poster/(?P<videoid>\d+)$', views.poster_view),
    url(r'^upload/', views.addvideo_view),
    # View to upload multiple videos with no foreign key to gloss.
    url(r'^add/$', views.addvideos_formview),
    # View that shows a list of glossvideos with no foreign key to gloss, user can add fk to gloss for glossvideos.
    url(r'^nogloss/', views.glossvideos_nogloss_listview),
    # View that updates a glossvideo
    url(r'^update/$', views.update_glossvideo_view),
    # View that handles the upload of poster file
    url(r'^add/poster$', views.add_poster_view, name='add_poster'),
]
