# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.urls import path, re_path, include
from django.contrib.auth.decorators import permission_required, login_required
from django.contrib import admin
from django.conf import settings
from django.contrib.sitemaps.views import sitemap
from django.views.static import serve

# Views
from django_registration.backends.activation.views import RegistrationView
from .dictionary.adminviews import GlossListView
from .tools import infopage
from django.contrib.flatpages import views as flatpages_views
from .comments import edit_comment, latest_comments, latest_comments_page, CommentListView, remove_tag
import notifications.urls
from .sitemaps import GlossSitemap, SignbankFlatPageSiteMap, StaticViewSitemap
# Forms
from .customregistration.forms import CustomUserForm

# Application namespace
app_name = 'signbank'

urlpatterns = [
    # Root page
    path('', flatpages_views.flatpage, {'url': '/'}, name='root_page'),

    path('sitemap.xml', sitemap, {'sitemaps': {'flatpages': SignbankFlatPageSiteMap,
                                                  'static': StaticViewSitemap,
                                                  'gloss': GlossSitemap, }},
        name='django.contrib.sitemaps.views.sitemap'),

    # This allows to change the translations site language
    path('i18n/', include('django.conf.urls.i18n')),

    # Include dictionary/, and video/ urls
    path('dictionary/',
        include('signbank.dictionary.urls', namespace='dictionary')),
    path('video/', include('signbank.video.urls', namespace='video')),

    # We used to have this url, keeping it in order to support old urls.
    path('signs/search/', permission_required('dictionary.search_gloss')(GlossListView.as_view()),
        name='sign_search'),

    # Registration urls for login, logout, registration, activation etc.
    path('accounts/register/', RegistrationView.as_view(form_class=CustomUserForm), name='django_registration_register',),
    path('accounts/', include('django_registration.backends.activation.urls')),
    path('accounts/', include('django.contrib.auth.urls')),

    # Django-contrib-comments urls
    path('comments/', include('django_comments.urls')),
    # Custom functionality added to comments app. Comment editing.
    path('comments/update/<int:id>/', login_required(edit_comment, login_url='/accounts/login/')),
    # Feed for latest comments.
    path('comments/latest/', permission_required('dictionary.search_gloss')(latest_comments),
        name='latest_comments'),
    # Page showing feed for latest comments. Count indicates how many comments to show.
    path('comments/latest/<int:count>/', permission_required('dictionary.search_gloss')(latest_comments_page),
        name='latest_comments_page'),
    path('comments/search/', permission_required('dictionary.search_gloss')(CommentListView.as_view()),
        name='search_comments'),
    path('comments/removetag/', permission_required('dictionary.search_gloss')(remove_tag),
        name='remove-comment-tag'),

    # Notifications urls
    path('inbox/notifications/', include(notifications.urls, namespace='notifications')),

    # Admin urls
    path('admin/doc/',
        include('django.contrib.admindocs.urls')),
    path('admin/', admin.site.urls),

    # Summernote urls, Summernote is the WYSIWYG editor currently used in Signbank
    path('summernote/', include('django_summernote.urls')),

    # Infopage, where we store some links and statistics
    path('info/', infopage, name='infopage'),
]
if settings.DEBUG:
    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', serve, {
            'document_root': settings.MEDIA_ROOT,
        }),
    ]
    try:
        import debug_toolbar
        # Add debug_toolbar when DEBUG=True, also add static+media folders when in development.
        # DEBUG should be False when in production!
        urlpatterns += [
            path('__debug__/', include(debug_toolbar.urls)),
        ]
    except (ImportError, ModuleNotFoundError):
        pass

# This is a catchall pattern, will try to match the rest of the urls with flatpages.
urlpatterns += [re_path('(?P<url>.*/)', flatpages_views.flatpage), ]  # Keep this as the last URL in the file!

