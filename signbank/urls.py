from django.conf.urls import url, include
from django.contrib.auth.decorators import permission_required
from django.contrib import admin
# Views
from django.contrib.auth import views as auth_views
from .pages import views as pages_views
from .dictionary import views as dictionary_views
from .dictionary.adminviews import GlossListView
from .feedback import views as feedback_views
from .tools import reload_signbank, infopage, refresh_videofilenames


admin.autodiscover()
from adminsite import publisher_admin

urlpatterns = [
    # Root page
    url(r'^$', pages_views.page,
        name='root_page'),

    # This allows to change the translations site language
    url(r'^i18n/', include('django.conf.urls.i18n')),

    # Include dictionary/, feedback/ and video/ urls
    url(r'^dictionary/',
        include('signbank.dictionary.urls', namespace='dictionary')),
    url(r'^feedback/', include('signbank.feedback.urls')),
    url(r'^video/', include('signbank.video.urls', namespace='video')),

    # Login and logout pages
    # TODO: django.contrib.auth.views.login and logout will be removed in django 1.11
    url(r'^login/', auth_views.login),
    url(r'^logout/', auth_views.logout,
        {'next_page': "/"}, "logout"),

    # Hardcoding a number of special urls:
    url(r'^signs/search/$', permission_required('dictionary.search_gloss')(GlossListView.as_view()),
        name='admin_gloss_list'),
    url(r'^signs/add/$', dictionary_views.add_new_sign),
    url(r'^signs/import_csv/$',
        dictionary_views.import_csv),
    url(r'^feedback/overview/$',
        feedback_views.showfeedback),

    url(r'^accounts/',
        include('signbank.registration.urls')),
    url(r'^admin/doc/',
        include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),

    # Speciall admin sub site for Publisher role
    url(r'^publisher/', include(publisher_admin.urls)),

    # Summernote urls, Summernote is the WYSIWYG editor currently used in Signbank
    url(r'^summernote/', include('django_summernote.urls')),

    # This URL runs a script on tools.py that reloads signbank app via 'touch signbank/wsgi.py'
    #url(r'reload_signbank/$',
    #    reload_signbank),

    # Infopage, where we store some links and statistics
    url(r'infopage/',
        infopage),

    # Incase you need to run this command from web (if for example only webserver has user rights to the folder)
    # uncomment the following line. It updates videofilenames to match the current filenaming policy.
    # url(r'refresh_videofilenames/$', refresh_videofilenames),

    # This url is meant to capture 'pages', so that we can use il8n language switching
    url(r'^(?P<url>.*)$',
        pages_views.page),
]
