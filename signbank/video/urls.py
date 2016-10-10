from django.conf.urls import url
# Views
from . import views

urlpatterns = [
    url(r'^(?P<videoid>\d+)$', views.video),
    url(r'^upload/', views.addvideo),
    url(r'^poster/(?P<videoid>\d+)$', views.poster),
]
