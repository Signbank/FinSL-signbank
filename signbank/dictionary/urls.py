# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import url
from django.views.generic.base import RedirectView
from django.contrib.auth.decorators import permission_required
# Views
from . import adminviews
from . import publicviews
from . import update
from . import delete
from . import views

urlpatterns = [
    # Public views for dictionary
    url(r'^$', publicviews.GlossListPublicView.as_view(), name='public_gloss_list'),
    url(r'^gloss/(?P<pk>\d+)', publicviews.GlossDetailPublicView.as_view(), name='public_gloss_view'),
    # Support old URLs, redirect them to new URLs.
    url(r'^public/gloss/$',
        RedirectView.as_view(pattern_name='dictionary:public_gloss_list', permanent=False)),
    url(r'^public/gloss/(?P<pk>\d+)',
        RedirectView.as_view(pattern_name='dictionary:public_gloss_view', permanent=False)),

    # Advanced search page
    url(r'^advanced/$', permission_required('dictionary.search_gloss')
        (adminviews.GlossListView.as_view()), name='admin_gloss_list'),

    # Main views for dictionary search page and gloss detail page, these used to be 'admin' views
    url(r'^advanced/list/$', permission_required('dictionary.search_gloss')(adminviews.GlossListView.as_view())),
    url(r'^advanced/gloss/(?P<pk>\d+)', permission_required('dictionary.search_gloss')
    (adminviews.GlossDetailView.as_view()), name='admin_gloss_view'),

    # GlossRelation search page
    url(r'^advanced/glossrelation/$', permission_required('dictionary.search_gloss')
    (adminviews.GlossRelationListView.as_view()), name='search_glossrelation'),
    # Redirect old URL
    url(r'^search/glossrelation/$', permission_required('dictionary.search_gloss')
    (RedirectView.as_view(pattern_name='dictionary:search_glossrelation', permanent=False))),

    # Create
    url(r'^advanced/gloss/create/$', views.create_gloss, name='create_gloss'),

    # Urls used to update data
    url(r'^update/gloss/(?P<glossid>\d+)$',
        update.update_gloss, name='update_gloss'),
    url(r'^update/tag/(?P<glossid>\d+)$',
        update.add_tag, name='add_tag'),
    url(r'^update/relation/$',
        update.add_relation, name='add_relation'),
    url(r'^update/relationtoforeignsign/$',
        update.add_relationtoforeignsign, name='add_relationtoforeignsign'),
    url(r'^update/morphologydefinition/$',
        update.add_morphology_definition, name='add_morphologydefinition'),
    url(r'^update/glossrelation/',
        update.gloss_relation, name='add_glossrelation'),

    url(r'^advanced/delete/glossurl/(?P<glossurl>\d+)$',
        delete.glossurl, name='delete_glossurl'),

    # CSV import urls
    url(r'^advanced/import/csv/$',
        update.import_gloss_csv, name='import_gloss_csv'),
    url(r'^advanced/import/csv/confirm/$',
        update.confirm_import_gloss_csv, name='confirm_import_gloss_csv'),

    # AJAX urls
    url(r'^ajax/keyword/(?P<prefix>.*)$',
        views.keyword_value_list),
    url(r'^ajax/gloss/(?P<prefix>.*)$',
        adminviews.gloss_ajax_complete, name='gloss_complete'),
    url(r'^ajax/searchresults/$',
        adminviews.gloss_ajax_search_results, name='ajax_search_results'),

    # XML ecv (externally controlled vocabulary) export for ELAN
    url(r'^ecv/(?P<dataset>\d+)$',
        adminviews.gloss_list_xml, name='gloss_list_xml'),

]
