from django.conf.urls import *
from signbank.dictionary.models import *

urlpatterns = patterns('',
                       # Feedback index
                       (r'^$', 'signbank.feedback.views.index'),

                       # Show feedback
                       (r'^show.html', 'signbank.feedback.views.showfeedback'),
                       (r'showfeedback/', 'signbank.feedback.views.showfeedback'),
                       # Missing sign feedback
                       (r'^missingsign.html',
                        'signbank.feedback.views.missingsign'),
                       (r'^missingsign/', 'signbank.feedback.views.missingsign'),
                       # General feedback about the site
                       (r'^generalfeedback.html',
                        'signbank.feedback.views.generalfeedback'),
                       (r'^site/', 'signbank.feedback.views.generalfeedback'),
                       # Sign feedback
                       (r'^sign/(?P<keyword>.+)-(?P<n>\d+).html$',
                        'signbank.feedback.views.signfeedback'),
                       # Gloss feedback
                       (r'^gloss/(?P<glossid>.+).html$',
                        'signbank.feedback.views.glossfeedback'),
                       # Some collection site of feedback, not sure what it is precisely
                       url(r'^interpreter/(?P<glossid>\d+)',
                           'signbank.feedback.views.interpreterfeedback', name='intnote'),
                       url(r'^interpreter.html',
                           'signbank.feedback.views.interpreterfeedback', name='intnotelist'),

                       # Delete feedback
                       (r'^(?P<kind>general|sign|missingsign)/delete/(?P<id>\d+)$',
                        'signbank.feedback.views.delete'),
                       )
