from django.conf.urls import *

urlpatterns = ['signbank.pages.views',
               (r'^(?P<url>.*)$', 'page'),
               ]
