# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import notifications.urls
from django.conf import settings
from django.contrib import admin
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.flatpages import views as flatpages_views
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path, re_path
# Views
from django.views.generic.base import TemplateView
from django_registration.backends.activation.views import RegistrationView

from .comments import (CommentListView, edit_comment, latest_comments,
                       latest_comments_page, remove_tag)
# Forms
from .customregistration.forms import CustomUserForm
from .customregistration.views import ActivationView
from .dictionary.adminviews import GlossListView
from .editorial_queue import get_queue_items
from .sitemaps import GlossSitemap, SignbankFlatPageSiteMap, StaticViewSitemap
from .tools import infopage

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
    path(
        "accounts/activate/complete/",
        TemplateView.as_view(
            template_name="django_registration/activation_complete.html"
        ),
        name="django_registration_activation_complete",
    ),
    path(
        "accounts/activate/<str:activation_key>/",
        ActivationView.as_view(),
        name="django_registration_activate",
    ),
    path('accounts/register/', RegistrationView.as_view(form_class=CustomUserForm),
         name='django_registration_register',),
    path('accounts/', include('django_registration.backends.activation.urls')),
    path('accounts/', include('django.contrib.auth.urls')),

    # Django-contrib-comments urls
    path('comments/', include('django_comments.urls')),
    # Custom functionality added to comments app. Comment editing.
    path('comments/update/<int:id>/',
         login_required(edit_comment, login_url='/accounts/login/')),
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
    path('inbox/notifications/',
         include(notifications.urls, namespace='notifications')),

    # Admin urls
    path('admin/doc/',
         include('django.contrib.admindocs.urls')),
    path('admin/', admin.site.urls),

    # Summernote urls, Summernote is the WYSIWYG editor currently used in Signbank
    path('summernote/', include('django_summernote.urls')),

    # Infopage, where we store some links and statistics
    path('info/', infopage, name='infopage'),

    # Editorial queue
    path('queue/', get_queue_items, name='queue'),
    path('queue/details/', get_queue_items, name='details'),
]
if settings.DEBUG:
    import debug_toolbar
    from django.conf.urls.static import static

    # Add debug_toolbar when DEBUG=True, also add static+media folders when in development.
    # DEBUG should be False when in production!
    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)\
        + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# This is a catchall pattern, will try to match the rest of the urls with flatpages.
# Keep this as the last URL in the file!
urlpatterns += [re_path('(?P<url>.*/)', flatpages_views.flatpage), ]
