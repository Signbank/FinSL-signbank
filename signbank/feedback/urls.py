from django.conf.urls import *

urlpatterns = [
    # Feedback index
    url(r'^$', 'signbank.feedback.views.index'),

    # Show feedback
    url(r'^show.html', 'signbank.feedback.views.showfeedback'),
    url(r'showfeedback/', 'signbank.feedback.views.showfeedback'),
    # Missing sign feedback
    url(r'^missingsign.html', 'signbank.feedback.views.missingsign'),
    url(r'^missingsign/', 'signbank.feedback.views.missingsign'),
    # General feedback about the site
    url(r'^generalfeedback.html', 'signbank.feedback.views.generalfeedback'),
    url(r'^site/', 'signbank.feedback.views.generalfeedback'),
    # Sign feedback
    url(r'^sign/(?P<keyword>.+)-(?P<n>\d+).html$', 'signbank.feedback.views.signfeedback'),
    # Gloss feedback
    url(r'^gloss/(?P<glossid>.+).html$', 'signbank.feedback.views.glossfeedback'),

    # Delete feedback
    url(r'^(?P<kind>general|sign|missingsign)/delete/(?P<id>\d+)$',
     'signbank.feedback.views.delete'),
]
