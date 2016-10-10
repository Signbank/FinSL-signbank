from django.conf.urls import url
from . import views

urlpatterns = [
    # Feedback index
    url(r'^$', views.index),

    # Show feedback
    url(r'^show.html', views.showfeedback),
    url(r'showfeedback/', views.showfeedback),
    # Missing sign feedback
    url(r'^missingsign.html', views.missingsign),
    url(r'^missingsign/', views.missingsign),
    # General feedback about the site
    url(r'^generalfeedback.html', views.generalfeedback),
    url(r'^site/', views.generalfeedback),
    # Sign feedback
    url(r'^sign/(?P<keyword>.+)-(?P<n>\d+).html$', views.signfeedback),
    # Gloss feedback
    url(r'^gloss/(?P<glossid>.+).html$', views.glossfeedback),

    # Delete feedback
    url(r'^(?P<kind>general|sign|missingsign)/delete/(?P<id>\d+)$', views.delete),
]
