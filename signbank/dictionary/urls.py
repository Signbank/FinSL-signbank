from django.conf.urls import *
from django.contrib.auth.decorators import permission_required

from signbank.dictionary.adminviews import GlossListView, GlossDetailView

urlpatterns = [
    # Gloss search url
    url(r'^search/$', permission_required('dictionary.search_gloss')
    (GlossListView.as_view()), name='menusearch'),

    # Urls used to update data
    url(r'^update/gloss/(?P<glossid>\d+)$',
        'signbank.dictionary.update.update_gloss', name='update_gloss'),
    url(r'^update/tag/(?P<glossid>\d+)$',
        'signbank.dictionary.update.add_tag', name='add_tag'),
    url(r'^update/definition/(?P<glossid>\d+)$',
        'signbank.dictionary.update.add_definition', name='add_definition'),
    url(r'^update/relation/$',
        'signbank.dictionary.update.add_relation', name='add_relation'),
    url(r'^update/relationtoforeignsign/$',
        'signbank.dictionary.update.add_relationtoforeignsign', name='add_relationtoforeignsign'),
    url(r'^update/morphologydefinition/$',
        'signbank.dictionary.update.add_morphology_definition', name='add_morphologydefinition'),
    url(r'^update/gloss/',
        'signbank.dictionary.update.add_gloss', name='add_gloss'),

    # AJAX urls
    url(r'^ajax/keyword/(?P<prefix>.*)$',
        'signbank.dictionary.views.keyword_value_list'),
    url(r'^ajax/tags/$',
        'signbank.dictionary.tagviews.taglist_json'),
    url(r'^ajax/gloss/(?P<prefix>.*)$',
        'signbank.dictionary.adminviews.gloss_ajax_complete', name='gloss_complete'),
    url(r'^ajax/searchresults/$',
        'signbank.dictionary.adminviews.gloss_ajax_search_results', name='ajax_search_results'),

    # Url to get list of glosses with selected tags
    url(r'^tag/(?P<tag>[^/]*)/?$',
        'signbank.dictionary.tagviews.taglist'),

    # XML ecv (externally controlled vocabulary) export for ELAN
    url(r'^ecv/(?P<dataset>\d+)$',
        'signbank.dictionary.adminviews.gloss_list_xml', name='gloss_list_xml'),

    # Main views for dictionary search page and gloss detail page, these used to be 'admin' views
    url(r'^list/$', permission_required('dictionary.search_gloss')(GlossListView.as_view())),
    url(r'^gloss/(?P<pk>\d+)', permission_required('dictionary.search_gloss')
    (GlossDetailView.as_view()), name='admin_gloss_view'),

    # These views are disabled simply because there is no use for them right now
    # url(r'^missingvideo.html$', 'signbank.dictionary.views.missing_video_view'),

    # A view for the developer to try out some things
    # url(r'^try/$', 'signbank.dictionary.views.try_code'),
]
