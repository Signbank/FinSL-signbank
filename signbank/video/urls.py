from django.conf.urls import url
from django.contrib.auth.decorators import permission_required
# Views
from . import views

urlpatterns = [
    url(r'^(?P<videoid>\d+)$', views.video),
    url(r'^poster/(?P<videoid>\d+)$', views.poster),
    url(r'^upload/', views.addvideo),
    # View to upload multiple videos with no foreign key to gloss.
    url(r'^add/$', permission_required('video.change_glossvideo')(views.AddVideosView.as_view())),
    # View that shows a list of glossvideos with no foreign key to gloss, user can add fk to gloss for glossvideos.
    url(r'^nogloss/', permission_required('video.change_glossvideo')(views.GlossVideosNoGlossListView.as_view())),
    # View that updates a glossvideo
    url(r'^update/$', permission_required('video.change_glossvideo')(views.update_glossvideo)),
]
