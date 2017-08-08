from __future__ import unicode_literals

from django.conf.urls import url
from django.contrib.auth.decorators import permission_required
# Views
from . import adminviews
from . import publicviews
from . import update
from . import views
from . import tagviews

urlpatterns = [
    # Gloss search url for the menu search field(s)
    url(r'^search/$', permission_required('dictionary.search_gloss')
    (adminviews.GlossListView.as_view()), name='menusearch'),

    # Urls used to update data
    url(r'^update/gloss/(?P<glossid>\d+)$',
        update.update_gloss, name='update_gloss'),
    url(r'^update/tag/(?P<glossid>\d+)$',
        update.add_tag, name='add_tag'),
    url(r'^update/definition/(?P<glossid>\d+)$',
        update.add_definition, name='add_definition'),
    url(r'^update/relation/$',
        update.add_relation, name='add_relation'),
    url(r'^update/relationtoforeignsign/$',
        update.add_relationtoforeignsign, name='add_relationtoforeignsign'),
    url(r'^update/morphologydefinition/$',
        update.add_morphology_definition, name='add_morphologydefinition'),
    url(r'^update/gloss/',
        update.add_gloss, name='add_gloss'),
    url(r'^update/glossrelation/',
        update.gloss_relation, name='add_glossrelation'),

    # CSV import urls
    url(r'^import/csv/$',
        update.import_gloss_csv, name='import_gloss_csv'),
    url(r'^import/csv/confirm/$',
        update.confirm_import_gloss_csv, name='confirm_import_gloss_csv'),

    # AJAX urls
    url(r'^ajax/keyword/(?P<prefix>.*)$',
        views.keyword_value_list),
    url(r'^ajax/tags/$',
        tagviews.taglist_json),
    url(r'^ajax/gloss/(?P<prefix>.*)$',
        adminviews.gloss_ajax_complete, name='gloss_complete'),
    url(r'^ajax/searchresults/$',
        adminviews.gloss_ajax_search_results, name='ajax_search_results'),

    # Url to get list of glosses with selected tags
    url(r'^tag/(?P<tag>[^/]*)/?$',
        tagviews.taglist),

    # XML ecv (externally controlled vocabulary) export for ELAN
    url(r'^ecv/(?P<dataset>\d+)$',
        adminviews.gloss_list_xml, name='gloss_list_xml'),

    # Main views for dictionary search page and gloss detail page, these used to be 'admin' views
    url(r'^list/$', permission_required('dictionary.search_gloss')(adminviews.GlossListView.as_view())),
    url(r'^gloss/(?P<pk>\d+)', permission_required('dictionary.search_gloss')
    (adminviews.GlossDetailView.as_view()), name='admin_gloss_view'),

    # Public views for dictionary
    url(r'^public/gloss/$', publicviews.GlossListPublicView.as_view(), name='public_gloss_list'),
    url(r'^public/gloss/(?P<pk>\d+)', publicviews.GlossDetailPublicView.as_view(), name='public_gloss_view'),

    # A view for the developer to try out some things
    # url(r'^try/$', views.try_code),
]
