# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import url, include
from django.contrib.auth.decorators import permission_required, login_required
from django.contrib import admin
from django.conf import settings

# Views
from registration.backends.hmac.views import RegistrationView
from .dictionary.adminviews import GlossListView
from .tools import infopage
from django.contrib.flatpages import views as flatpages_views
from .comments import edit_comment, latest_comments, latest_comments_page, CommentListView, remove_tag
import notifications.urls
# Forms
from .customregistration.forms import CustomUserForm

# Application namespace
app_name = 'signbank'

urlpatterns = [
    # Root page
    url(r'^$', flatpages_views.flatpage, {'url': '/'},
        name='root_page'),

    # This allows to change the translations site language
    url(r'^i18n/', include('django.conf.urls.i18n')),

    # Include dictionary/, and video/ urls
    url(r'^dictionary/',
        include('signbank.dictionary.urls', namespace='dictionary')),
    url(r'^video/', include('signbank.video.urls', namespace='video')),

    # We used to have this url, keeping it in order to support old urls.
    url(r'^signs/search/$', permission_required('dictionary.search_gloss')(GlossListView.as_view()),
        name='sign_search'),

    # Registration urls for login, logout, registration, activation etc.
    url(r'^accounts/register/$', RegistrationView.as_view(form_class=CustomUserForm), name='registration_register',),
    url(r'^accounts/', include('registration.backends.hmac.urls')),

    # Django-contrib-comments urls
    url(r'^comments/', include('django_comments.urls')),
    # Custom functionality added to comments app. Comment editing.
    url(r'^comments/update/(?P<id>\d+)/$', login_required(edit_comment, login_url='/accounts/login/')),
    # Feed for latest comments.
    url(r'^comments/latest/$', permission_required('dictionary.search_gloss')(latest_comments),
        name='latest_comments'),
    # Page showing feed for latest comments. Count indicates how many comments to show.
    url(r'^comments/latest/(?P<count>\d+)/$', permission_required('dictionary.search_gloss')(latest_comments_page),
        name='latest_comments_page'),
    url(r'^comments/search/$', permission_required('dictionary.search_gloss')(CommentListView.as_view()),
        name='search_comments'),
    url(r'^comments/removetag/$', permission_required('dictionary.search_gloss')(remove_tag),
        name='remove-comment-tag'),

    # Notifications urls
    url('^inbox/notifications/', include(notifications.urls, namespace='notifications')),

    # Admin urls
    url(r'^admin/doc/',
        include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),

    # Summernote urls, Summernote is the WYSIWYG editor currently used in Signbank
    url(r'^summernote/', include('django_summernote.urls')),

    # Infopage, where we store some links and statistics
    url(r'info/', infopage, name='infopage'),
]
if settings.DEBUG:
    import debug_toolbar
    from django.conf.urls.static import static
    # Add debug_toolbar when DEBUG=True, also add static+media folders when in development.
    # DEBUG should be False when in production!
    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)\
        + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# This is a catchall pattern, will try to match the rest of the urls with flatpages.
urlpatterns += [url(r'^(?P<url>.*/)$', flatpages_views.flatpage), ]  # Keep this as the last URL in the file!

