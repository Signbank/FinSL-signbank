from django.conf.urls import *
from django.conf import settings
from django.contrib.auth.decorators import login_required, permission_required
import registration.forms
from django.conf.urls.static import static
from django.views.generic import TemplateView

from signbank.dictionary.models import Gloss
from signbank.dictionary.adminviews import GlossListView, GlossDetailView

from django.contrib import admin
admin.autodiscover()

from adminsite import publisher_admin

# TODO: Remove this
if settings.SHOW_NUMBERSIGNS:
    numbersigns_view = TemplateView.as_view(
        template_name='numbersigns/numbersigns.html')
else:
    numbersigns_view = TemplateView.as_view(
        template_name='numbersigns/underconstruction.html')


urlpatterns = patterns('',

                       url(r'^$', 'signbank.pages.views.page',
                           name='root_page'),

                       # This allows to change the translations site language
                       url(r'^i18n/', include('django.conf.urls.i18n')),

                       url(r'^dictionary/',
                           include('signbank.dictionary.urls', namespace='dictionary')),
                       url(r'^feedback/', include('signbank.feedback.urls')),

                       url(r'^video/', include('signbank.video.urls')),

                       #(r'^register.html', 'signbank.views.index'),
                       url(r'^logout.html', 'django.contrib.auth.views.logout',
                           {'next_page': "/"}, "logout"),

                       # Hardcoding a number of special urls:
                       url(r'^signs/dictionary/$',
                           'signbank.dictionary.views.search'),
                       url(r'^signs/search/$', permission_required('dictionary.search_gloss')
                           (GlossListView.as_view())),
                       url(r'^signs/add/$', 'signbank.dictionary.views.add_new_sign'),
                       url(r'^signs/import_csv/$',
                           'signbank.dictionary.views.import_csv'),
                       url(r'^feedback/overview/$',
                           'signbank.feedback.views.showfeedback'),

                       # (r'^accounts/login/', 'django.contrib.auth.views.login'),

                       url(r'^accounts/',
                           include('signbank.registration.urls')),
                       url(r'^admin/doc/',
                           include('django.contrib.admindocs.urls')),
                       url(r'^admin/', include(admin.site.urls)),

                       # special admin sub site
                       url(r'^publisher/', include(publisher_admin.urls)),

                       url(r'^summernote/', include('django_summernote.urls')),

                       # This URL runs a script on tools.py that reloads signbank app
                       # It simply runs: 'touch signbank/wsgi.py'
                       url(r'reload_signbank/$',
                           'signbank.tools.reload_signbank'),

                       # TODO: Review the sanity of this implementation, it sounds completely crazy, but it also works
                       # This URL is supposed to grab every url not grabbed by any url before.
                       # The reason is to forward user created static pages inside the app to a view 'page'.
                       url(r'(.*)',
                           'signbank.pages.views.page'),

                       ) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
