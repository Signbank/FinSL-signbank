from django.conf.urls import url
# Views
from . import views

urlpatterns = [
               url(r'^(?P<url>.*)$', views.page),
               ]
