# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import csv
import json
from collections import defaultdict

import djqscsv
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.aggregates import StringAgg
from django.core.exceptions import PermissionDenied
from django.db.models import Count, F, OuterRef, Prefetch, Q, Value
from django.db.models.fields import CharField, NullBooleanField
from django.db.models.functions import Concat
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.utils.translation import get_language
from django.utils.translation import ugettext as _
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from guardian.shortcuts import (get_objects_for_user, get_perms,
                                get_users_with_perms)
from reversion.models import Version
from tagging.models import Tag, TaggedItem

from ..comments import CommentTagForm
from ..video.forms import GlossVideoForGlossForm
from ..video.models import GlossVideo
from .forms import (GlossRelationForm, GlossRelationSearchForm,
                    GlossSearchForm, MorphologyForm, RelationForm, TagsAddForm)
from .models import (Dataset, FieldChoice, Gloss, GlossRelation,
                     GlossTranslations, GlossURL, Lemma, MorphologyDefinition,
                     Relation, RelationToForeignSign, Translation)


class GlossListView(ListView):
    model = Gloss
    template_name = 'dictionary/admin_gloss_list.html'
    paginate_by = 100

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(GlossListView, self).get_context_data(**kwargs)
        # Add in a QuerySet
        context['searchform'] = GlossSearchForm(self.request.GET)
        # Get allowed datasets for user (django-guardian)
        allowed_datasets = get_objects_for_user(
            self.request.user, 'dictionary.view_dataset')
        # Filter the forms dataset field for the datasets user has permission to.
        context['searchform'].fields["dataset"].queryset = Dataset.objects.filter(
            id__in=[x.id for x in allowed_datasets])

        populate_tags_for_object_list(
            context['object_list'], model=self.object_list.model)

        if 'order' not in self.request.GET:
            context['order'] = 'idgloss'
        else:
            context['order'] = self.request.GET.get('order')

        return context

    def get_paginate_by(self, queryset):
        """
        Paginate by specified value in querystring, or use default class property value.
        """
        return self.request.GET.get('paginate_by', self.paginate_by)

    def render_to_response(self, context, **kwargs):

        # Look for a 'format=json' GET argument
        if self.request.GET.get("format") == "CSV-standard":
            return self.subquery_render_to_csv_response(context)
        elif self.request.GET.get("format") == "CSV-ready-for-validation":
            return self.ready_for_validation_render_to_csv_response(context)
        else:
            return super(GlossListView, self).render_to_response(context)

    #
    # NOTE to future devs.
    # The reason the code below is prefixed 'subquery' is that, for speed, we use Django
    # annotated subqueries here to push as much of the work onto Postgres as we can.
    #
    # The old code was prefixed 'pythonic', because it worked by analysing the returned results
    # in python code, using nested loops.
    # This was slow, even after optimisation, and on a fast system a full query took over 20 seconds
    # to complete. At writing our Heroku timeout limit is 30 seconds, and the client did in fact get
    # timeouts sometimes, which made us develop this Postgres low-level version.
    #
    # The old 'pythonic' code may be found at this commit:
    # https://github.com/ODNZSL/NZSL-signbank/commit/3ec77f1694350801ce29a21e8e6cfd61cc21523e
    #
    # Some fields were too hard to retrieve via subquery, eg. 'keywords', a deprecated field, which was
    # an amalgamation of all translations. If devs strike a situation in future where they need to
    # retrieve an especially complex field, this will probably have to be implemented 'pythonically'.
    # It is presumed that the speedup provided by the Postgres subquery approach will sufficiently
    # offset any slowdown that results.
    #

    # Field in Signbank -> Field in NZSL Dictionary
    # These are in the order that Micky Vale specified NZSL want them in.
    # Please keep any redundant entries (eg. 'id' -> 'id'), as a reminder of that field ordering.
    # ForeignKey fields on the left need to use double-underscore filter syntax -
    #  eg. strong_handshape__english_name for accessing FieldChoices.
    # The left fields that end in _aggregate are aliases used in annotated subqueries, see below.
    subquery_signbank_field_to_dictionary_field = {
        'id':                               'id',                           # Signbank ID
        'dataset__name':                    'dataset',                      # Dataset
        'variant_no':                       'variant_number',

        # aggregated multi-value fields
        'gloss_main_aggregate':             'gloss_main',                   # Gloss
        'gloss_secondary_aggregate':        'gloss_secondary',
        'gloss_minor_aggregate':            'gloss_minor',

        'gloss_maori_aggregate':            'gloss_maori',                  # Gloss Māori
        'strong_handshape__english_name':   'handshape',
        'location__english_name':           'location_name',
        'one_or_two_hand':                  'one_or_two_handed',

        # aggregated multi-value field
        'wordclasses_aggregate':            'word_classes',

        'inflection_manner_degree':         'inflection_manner_and_degree',
        'inflection_temporal':              'inflection_temporal',
        'inflection_plural':                'inflection_plural',
        'directional':                      'is_directional',
        'locatable':                        'is_locatable',
        'number_incorporated':              'contains_numbers',
        'fingerspelling':                   'is_fingerspelling',
        'videoexample1':                   'videoexample1',
        'videoexample1_translation':       'videoexample1_translation',
        'videoexample2':                   'videoexample2',
        'videoexample2_translation':       'videoexample2_translation',
        'videoexample3':                   'videoexample3',
        'videoexample3_translation':       'videoexample3_translation',
        'videoexample4':                   'videoexample4',
        'videoexample4_translation':       'videoexample4_translation',
        'hint':                             'hint',
        'notes':                            'usage_notes',                  # Notes
        'age_variation__english_name':      'age_groups',
        'relationtoforeignsign__other_lang':'related_to',
        'usage__english_name':              'usage',

        # aggregated multi-value field
        'semantic_field_aggregate':         'semantic_field',

        # The fields below are not necessary but Micky Vale is happy for them to remain
        'dataset__signlanguage__name':      'signlanguage',
        # keywords - in the old system this was an aggregation of all translations.
        # It proved too difficult to reproduce using annotated subqueries.
        #'keywords'                         'keywords'
        'created_at':                       'created_at',
        'created_by__username':             'created_by',
        'updated_at':                       'updated_at',
        'updated_by__username':             'updated_by',
        }

    # string delimeter for aggregated multi-value fields
    CSV_AGG_DELIM = "; "

    def subquery_render_to_csv_response(self, context):
        if not self.request.user.has_perm('dictionary.export_csv'):
            msg = _("You do not have permissions to export to CSV.")
            messages.error(self.request, msg)
            raise PermissionDenied(msg)

        # Create the HttpResponse object with the appropriate CSV header.
        # It is a Python file-like object.
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename="dictionary-export.csv"'

        # Set up for outputting CSV.
        writer = csv.writer(response)

        # For speed, we use Django annotated subqueries here to push as much of the work onto Postgres as we can.
        # StringAgg() is a Postgres-specific function exposed in Django.
        # Refs used:
        # https://docs.djangoproject.com/en/4.0/ref/contrib/postgres/aggregates/#stringagg
        # https://docs.djangoproject.com/en/4.0/ref/models/expressions/
        # Some pre-fetching optimizations are already performed by get_queryset().
        csv_queryset = self.get_queryset()\
            .select_related('dataset', 'created_by', 'updated_by', 'strong_handshape', 'location', 'age_variation')\
            .prefetch_related('glosstranslations_set', 'relationtoforeignsign_set',\
                              'usage', 'wordclasses', 'semantic_field')\
            .annotate(
                gloss_main_aggregate=StringAgg(
                    GlossTranslations.objects.filter(
                        gloss=OuterRef('pk'),
                        language__language_code_2char='EN').
                        values('translations')[:1],
                    self.CSV_AGG_DELIM,
                    distinct=True,
                    output_field=CharField()
                ),
                gloss_secondary_aggregate=StringAgg(
                    GlossTranslations.objects.filter(
                        gloss=OuterRef('pk'),
                        language__language_code_2char='EN'
                    ).values('translations_secondary')[:1],
                    self.CSV_AGG_DELIM,
                    distinct=True,
                    output_field=CharField()
                ),
                gloss_minor_aggregate=StringAgg(
                    GlossTranslations.objects.filter(
                        gloss=OuterRef('pk'),
                        language__language_code_2char='EN'
                    ).values('translations_minor')[:1],
                    self.CSV_AGG_DELIM,
                    distinct=True,
                    output_field=CharField()
                ),
                gloss_maori_aggregate=StringAgg(
                    GlossTranslations.objects.filter(
                        gloss=OuterRef('pk'),
                        language__language_code_2char='MI'
                    ).values('translations')[:1],
                    self.CSV_AGG_DELIM,
                    distinct=True,
                    output_field=CharField()
                ),
                semantic_field_aggregate=StringAgg('semantic_field__english_name', self.CSV_AGG_DELIM, distinct=True),
                wordclasses_aggregate=StringAgg('wordclasses__english_name', self.CSV_AGG_DELIM, distinct=True)
            )\
            .values(*self.subquery_signbank_field_to_dictionary_field.keys())

        # Column headers.
        writer.writerow(self.subquery_signbank_field_to_dictionary_field.values())

        # NOTE The following loop is almost exactly what the djqscsv module does internally.
        # We tried using the djqscsv module, with similar annotated subqueries to the above,
        # but discovered we needed more control. Hence we have fallen back on a semi-manual system here.
        # It is still extremely fast.
        for queryset_values_record in csv_queryset:
            arr = []
            items_dict = dict(queryset_values_record.items())
            # force ordering
            for field_name in self.subquery_signbank_field_to_dictionary_field.keys():
                try:
                    items_field = items_dict[field_name]
                    if items_field == None:
                        items_field = ''
                    arr.append(str(items_field))
                except:
                    arr.append('')
            writer.writerow(arr)

        return response

    def ready_for_validation_render_to_csv_response(self, context):
        if not self.request.user.has_perm("dictionary.export_csv"):
            msg = _("You do not have permissions to export to CSV.")
            messages.error(self.request, msg)
            raise PermissionDenied(msg)

        # Create the HttpResponse object with the appropriate CSV header.
        # It is a Python file-like object.
        response = HttpResponse(content_type="text/csv; charset=utf-8")
        response[
            "Content-Disposition"
        ] = 'attachment; filename="ready-for-validation-export.csv"'

        # Set up for outputting CSV.
        writer = csv.writer(response)

        # The queryset may or may not already be filtered for the ready for validation tag.
        # We have to make sure it is filtered by the tag, so we are filtering again
        ready_for_validation_qs = TaggedItem.objects.get_by_model(
            self.get_queryset(),
            settings.TAG_READY_FOR_VALIDATION
        )

        gloss_video_qs = GlossVideo.objects.select_related("video_type").filter(
            video_type__isnull=False,
            video_type__field="video_type",
            video_type__english_name="validation",
            videofile__isnull=False,
            is_public=True,
        )

        csv_queryset = (
            ready_for_validation_qs
            .prefetch_related(
                "glosstranslations_set",
                Prefetch(
                    "glossvideo_set", queryset=gloss_video_qs, to_attr="validation_videos"
                )
            )
            .annotate(
                gloss_main_aggregate=StringAgg(
                    GlossTranslations.objects.filter(
                        gloss=OuterRef("pk"),
                        language__language_code_2char="EN"
                    ).values("translations")[:1],
                    self.CSV_AGG_DELIM,
                    distinct=True,
                    output_field=CharField()
                ),
            )
        )

        headers = [
            "idgloss",
            "gloss_main",
            "video_url"
        ]
        writer.writerow(headers)

        for gloss_record in csv_queryset:
            row = [gloss_record.idgloss, gloss_record.gloss_main_aggregate]
            try:
                validation_video = gloss_record.validation_videos[0]
                row.append(validation_video.videofile.storage.public_url(validation_video.videofile.name))
            except IndexError:
                row.append("")
            writer.writerow(row)

        return response

    def get_queryset(self):
        # get query terms from self.request
        qs = Gloss.objects.all()

        # Filter in only objects in the datasets the user has permissions to.
        allowed_datasets = get_objects_for_user(
            self.request.user, 'dictionary.view_dataset')
        qs = qs.filter(dataset__in=allowed_datasets)

        get = self.request.GET

        # Search for multiple datasets (if provided)
        vals = get.getlist('dataset', [])
        if vals != []:
            qs = qs.filter(dataset__in=vals)

        if 'search' in get and get['search'] != '':
            val = get['search']
            # Searches for multiple fields at the same time. Looking if any of the fields match.
            query = (Q(idgloss__icontains=val) | Q(idgloss_mi__icontains=val) | Q(notes__icontains=val) |
                     Q(translation__keyword__text__icontains=val))
            qs = qs.filter(query)

        if 'gloss' in get and get['gloss'] != '':
            val = get['gloss']
            # Search for glosses starting with a string, case sensitive
            query = Q(idgloss__istartswith=val)
            qs = qs.filter(query)

        if 'idgloss_mi' in get and get['idgloss_mi'] != '':
            val = get['idgloss_mi']
            qs = qs.filter(idgloss_mi__istartswith=val)
        if 'keyword' in get and get['keyword'] != '':
            if 'trans_lang' in get and get['trans_lang'] != '':
                val = get['keyword']
                lang = get['trans_lang']
                qs = qs.filter(
                    translation__keyword__text__icontains=val, translation__language__in=lang)

        if 'published' in get and get['published'] != '':
            val = get['published'] == 'on'
            qs = qs.filter(published=val)

        # If get has both keys hasvideo and hasnovideo, don't use them to query.
        if not ('hasvideo' in get and 'hasnovideo' in get):
            if 'hasvideo' in get and get['hasvideo'] != '':
                val = get['hasvideo'] != 'on'
                qs = qs.filter(glossvideo__isnull=val)

            if 'hasnovideo' in get and get['hasnovideo'] != '':
                val = get['hasnovideo'] == 'on'
                qs = qs.filter(glossvideo__isnull=val)

        # If gloss has multiple GlossVideos
        if 'multiplevideos' in get and get['multiplevideos'] != '' and get['multiplevideos'] == 'on':
            # Include glosses that have more than one GlossVideo
            qs = qs.annotate(videocount=Count('glossvideo')
                             ).filter(videocount__gt=1)

        # A list of phonology fieldnames
        fieldnames = ['handedness', 'strong_handshape', 'weak_handshape', 'location', 'relation_between_articulators',
                      'absolute_orientation_palm', 'absolute_orientation_fingers', 'relative_orientation_movement',
                      'relative_orientation_location', 'orientation_change', 'handshape_change', 'repeated_movement',
                      'alternating_movement', 'movement_shape', 'movement_direction', 'movement_manner',
                      'contact_type', 'phonology_other', 'mouth_gesture', 'mouthing', 'phonetic_variation',
                      'iconic_image', 'named_entity', 'number_of_occurences', 'fingerspelling',
                      'one_or_two_hand', 'number_incorporated', 'locatable', 'directional', 'variant_no']

        # Language and basic property filters
        vals = get.getlist('dialect', [])
        if vals != []:
            qs = qs.filter(dialect__in=vals)

        vals = get.getlist('language', [])
        if vals != []:
            # Get languages from dataset
            qs = qs.filter(dataset__language__in=vals)

        if 'notes' in get and get['notes'] != '':
            qs = qs.filter(notes__icontains=get['notes'])

        if 'semantic_field' in get and get['semantic_field'] != '':
            vals = get.getlist('semantic_field')
            qs = qs.filter(semantic_field__id__in=vals)

        # phonology and semantics field filters
        for fieldname in fieldnames:
            if fieldname in get:
                key = fieldname + '__exact'
                val = get[fieldname]
                if isinstance(Gloss._meta.get_field(fieldname), NullBooleanField):
                    val = {'0': '', '1': None, '2': True, '3': False}[val]

        if 'tags' in get and get['tags'] != '':
            vals = get.getlist('tags')

            tags = []
            for t in vals:
                tags.extend(Tag.objects.filter(pk=t))

            # search is an implicit AND so intersection
            tqs = TaggedItem.objects.get_intersection_by_model(Gloss, tags)

            # intersection
            qs = qs & tqs

            # print "J :", len(qs)

        qs = qs.distinct()

        if 'nottags' in get and get['nottags'] != '':
            vals = get.getlist('nottags')

            # print "NOT TAGS: ", vals

            tags = []
            for t in vals:
                tags.extend(Tag.objects.filter(name=t))

            # search is an implicit AND so intersection
            tqs = TaggedItem.objects.get_intersection_by_model(Gloss, tags)

            # print "NOT", tags, len(tqs)
            # exclude all of tqs from qs
            qs = [q for q in qs if q not in tqs]

            # print "K :", len(qs)

        if 'relation_to_foreign_signs' in get and get['relation_to_foreign_signs'] != '':
            val = get['relation_to_foreign_signs']
            gloss_ids = RelationToForeignSign.objects.filter(
                other_lang=val).values_list('gloss_id', flat=True)
            qs = qs.filter(id__in=gloss_ids)

        if 'location' in get and get['location'] != '':
            val = get['location']
            qs = qs.filter(location=val)

        if 'one_or_two_handed' in get and get['one_or_two_handed'] != '':
            val = get['one_or_two_handed'] == 'on'
            qs = qs.filter(one_or_two_hand=val)

        if 'example_search' in get and get['example_search'] != '':
            """
                This search is intended to search for gloss IDs in fields videoexample1 to videoexample4. In these
                fields, gloss IDs are within square brackets (eg: cat[123], 123 is the gloss ID).
                When we search for a gloss ID (eg: 123), the search should return all the glosses that contain gloss ID
                123 in one of their videoexample fields.
                Search parameter is just the gloss id, so we are adding []s before doing the search.
            """

            val = get['example_search']
            val = '[' + val + ']'

            query = (Q(videoexample1__icontains=val) | Q(videoexample2__icontains=val) | Q(videoexample3__icontains=val) |
                     Q(videoexample4__icontains=val))
            qs = qs.filter(query)

        if 'age_variation' in get and get['age_variation'] != '':
            val = get['age_variation']
            qs = qs.filter(age_variation=val)

        if 'handedness' in get and get['handedness'] != '':
            val = get['handedness']
            qs = qs.filter(handedness=val)

        if 'strong_handshape' in get and get['strong_handshape'] != '':
            val = get['strong_handshape']
            qs = qs.filter(strong_handshape=val)

        if 'word_classes' in get and get['word_classes'] != '':
            vals = get.getlist('word_classes')
            qs = qs.filter(wordclasses__id__in=vals)

        if 'number_incorporated' in get and get['number_incorporated'] != '':
            val = get['number_incorporated'] == 'on'
            qs = qs.filter(number_incorporated=val)

        if 'locatable' in get and get['locatable'] != '':
            val = get['locatable'] == 'on'
            qs = qs.filter(locatable=val)

        if 'directional' in get and get['directional'] != '':
            val = get['directional'] == 'on'
            qs = qs.filter(directional=val)

        if 'fingerspelling' in get and get['fingerspelling'] != '':
            val = get['fingerspelling'] == 'on'
            qs = qs.filter(fingerspelling=val)

        if 'inflection_temporal' in get and get['inflection_temporal'] != '':
            val = get['inflection_temporal'] == 'on'
            qs = qs.filter(inflection_temporal=val)

        if 'inflection_manner_degree' in get and get['inflection_manner_degree'] != '':
            val = get['inflection_manner_degree'] == 'on'
            qs = qs.filter(inflection_manner_degree=val)

        if 'inflection_plural' in get and get['inflection_plural'] != '':
            val = get['inflection_plural'] == 'on'
            qs = qs.filter(inflection_plural=val)

        if 'relation' in get and get['relation'] != '':
            potential_targets = Gloss.objects.filter(
                idgloss__icontains=get['relation'])
            relations = Relation.objects.filter(target__in=potential_targets)
            potential_pks = [relation.source.pk for relation in relations]
            qs = qs.filter(pk__in=potential_pks)

        if 'hasRelation' in get and get['hasRelation'] != '':

            # Find all relations with this role
            if get['hasRelation'] == 'all':
                relations_with_this_role = Relation.objects.all()
            else:
                relations_with_this_role = Relation.objects.filter(
                    role__exact=get['hasRelation'])

            # Remember the pk of all glosses that take part in the collected
            # relations
            pks_for_glosses_with_correct_relation = [
                relation.source.pk for relation in relations_with_this_role]
            qs = qs.filter(pk__in=pks_for_glosses_with_correct_relation)

        if 'morpheme' in get and get['morpheme'] != '':
            potential_morphemes = Gloss.objects.filter(
                idgloss__icontains=get['morpheme'])
            potential_morphdefs = MorphologyDefinition.objects.filter(
                morpheme__in=[morpheme.pk for morpheme in potential_morphemes])
            potential_pks = [
                morphdef.parent_gloss.pk for morphdef in potential_morphdefs]
            qs = qs.filter(pk__in=potential_pks)

        if 'hasMorphemeOfType' in get and get['hasMorphemeOfType'] != '':
            morphdefs_with_correct_role = MorphologyDefinition.objects.filter(
                role__exact=get['hasMorphemeOfType'])
            pks_for_glosses_with_morphdefs_with_correct_role = [
                morphdef.parent_gloss.pk for morphdef in morphdefs_with_correct_role]
            qs = qs.filter(
                pk__in=pks_for_glosses_with_morphdefs_with_correct_role)

        # Filter by usage
        if 'usage' in get and get['usage'] != '':
            vals = get.getlist('usage')
            qs = qs.filter(usage__id__in=vals)

        # Set order according to GET field 'order'
        if 'order' in get:
            qs = qs.order_by(get['order'])
        else:
            qs = qs.order_by('idgloss')

        # Prefetching translation and dataset objects for glosses to minimize the amount of database queries.
        qs = qs.prefetch_related(Prefetch('translation_set', queryset=Translation.objects.filter(
            language__language_code_2char__iexact=get_language()).select_related('keyword')),
            Prefetch('dataset'),
            # Ordering by version to get the first versions posterfile.
            Prefetch('glossvideo_set', queryset=GlossVideo.objects.all().order_by('version')))

        # Saving querysets results to sessions, these results can then be used elsewhere (like in gloss_detail)
        # Flush the previous queryset (just in case)
        self.request.session['search_results'] = None

        # Check if QuerySet has filters applied (user is searching for something)
        # TODO: Future me or future other developer, it could be useful to find a better way to do this, if one exists
        if hasattr(qs.query.where, 'children') and len(qs.query.where.children) > 1:
            # This comparison has been changed from >0 to >1 due to checking for WHERE dataset.id IN.
            items = []
            for item in qs:
                items.append(dict(id=item.id, gloss=item.idgloss))

            self.request.session['search_results'] = items

        return qs


def populate_tags_for_object_list(object_list, model):
    """Inserts tags for each item in a list of objects."""
    # Get the ContentType for the model.
    content_type = ContentType.objects.get_for_model(model)
    # Get TaggedItems of selected ContentType for all the list items that have TaggedItems.
    tagged_items = TaggedItem.objects.filter(content_type=content_type,
                                             object_id__in=[obj.pk for obj in object_list])
    tagged_items = tagged_items.select_related('tag')
    tags_map = defaultdict(list)
    for tagged_item in tagged_items:
        tags_map[tagged_item.object_id].append(tagged_item.tag)
        for obj in object_list:
            obj.cached_tags = tags_map[obj.pk]


def populate_tags_for_queryset(queryset):
    """Inserts tags for each item in queryset."""
    # Get the ContentType for the queryset objects.
    content_type = ContentType.objects.get_for_model(queryset.model)
    # Get TaggedItems of selected ContentType for all the queryset items that have TaggedItems.
    tagged_items = TaggedItem.objects.filter(content_type=content_type,
                                             object_id__in=queryset.values_list('pk', flat=True))
    tagged_items = tagged_items.select_related('tag')
    tags_map = defaultdict(list)
    for tagged_item in tagged_items:
        tags_map[tagged_item.object_id].append(tagged_item.tag)
        for obj in queryset:
            obj.cached_tags = tags_map[obj.pk]


class GlossDetailView(DetailView):
    model = Gloss
    context_object_name = 'gloss'

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        # Check that the user has object level permission (django-guardian) to this objects dataset object.
        if 'view_dataset' not in get_perms(request.user, obj.dataset):
            msg = _("You do not have permissions to view glosses of this dataset.")
            messages.error(request, msg)
            raise PermissionDenied(msg)
        return super(GlossDetailView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(GlossDetailView, self).get_context_data(**kwargs)
        gloss = context['gloss']
        dataset = gloss.dataset
        context['dataset'] = dataset
        context['dataset_users'] = list(get_users_with_perms(
            dataset).values_list('username', flat=True))
        context['tagsaddform'] = TagsAddForm()
        context['commenttagform'] = CommentTagForm()
        context['glossvideoform'] = GlossVideoForGlossForm()
        context['field_choices'] = Gloss.get_choice_lists()

        context['assignable_users'] = list(
            User.objects
                .filter(is_staff=True, is_active=True)
                .annotate(full_name=Concat(F('first_name'), Value(' '), F('last_name'), output_field=CharField()))
                .values(label=F('full_name'), value=F('id')))

        context['lemmas'] = list(Lemma.objects.values('name'))
        context['relationform'] = RelationForm()
        context['morphologyform'] = MorphologyForm()
        context['glossrelationform'] = GlossRelationForm(
            initial={'source': gloss.id, })
        # Choices for GlossRelationForm
        context['dataset_glosses'] = json.dumps(list(Gloss.objects.filter(
            dataset=dataset).values(label=F('idgloss'), value=F('id'))))
        # GlossRelations for this gloss
        context['glossrelations'] = GlossRelation.objects.filter(source=gloss)
        context['glossrelations_reverse'] = GlossRelation.objects.filter(
            target=gloss)
        context['glossurls'] = GlossURL.objects.filter(gloss=gloss)
        context['translation_languages_and_translations'] = gloss.get_translations_for_translation_languages()

        if self.request.user.is_staff:

            # Using the Reversion middleware, get version history data:
            # This is an iterable of Version instance, each of which contains data including:
            #   * A dict of fieldname => field for this model (in this case Gloss)
            #   * A Revision instance with:
            #       Metadata stored when the Version was created
            #       References to the state of all other model instances under Reversion control at the time the Version was saved
            #           (eg. Translation instances)
            version_history = Version.objects.get_for_object(
                gloss).prefetch_related('revision__user')

            # Get ContentType for Translation model so we can retrieve Translation instance states from Reversion
            translation_contenttype = ContentType.objects.get_for_model(
                Translation)

            revisions = []
            revisions_ignore = ('updated_at')
            gloss_fieldchoice_fields = ['handedness', 'strong_handshape', 'weak_handshape', 'location', 'relation_between_articulators',
                                        'absolute_orientation_palm', 'absolute_orientation_fingers', 'relative_orientation_movement',
                                        'relative_orientation_location', 'orientation_change', 'handshape_change', 'movement_shape',
                                        'movement_direction', 'movement_manner', 'contact_type', 'wordclasses', 'usage', 'named_entity',
                                        'semantic_field', 'signer', 'age_variation']

            # Determine which fields have changed
            for i, version_hist_entry in enumerate(version_history):
                if i+1 >= len(version_history):
                    continue

                # Regular fields
                for key, value in version_hist_entry.field_dict.items():
                    if key in revisions_ignore:
                        continue

                    changed_new = value
                    changed_old = version_history[i+1].field_dict[key]

                    if changed_new != changed_old:

                        # Reversion gives us the field name, which for a ForeignKey is sometimes the db column name with '_id'
                        # NOTE removesuffix() is new in Python 3.9
                        keycut = key.removesuffix('_id')

                        # Use the raw field name (key) to retrieve the field verbose name
                        # This works in Django regardless of whether the key is a field name or db column name
                        changed_field_verbosename = Gloss._meta.get_field(
                            key).verbose_name

                        if keycut in gloss_fieldchoice_fields:

                            # If we were given a straight FieldChoice field name, then the values contained in the revision
                            # are primary keys of FieldChoice records.
                            # But if we were given a dictionary_fieldchoice db column name - ie. if it had '_id' on the end - then
                            # the value in the revision is a (single, unique) machine_value number instead.
                            # We have to adjust our QuerySet filters accordingly.
                            if key != keycut:
                                changed_old_qs = FieldChoice.objects.filter(
                                    machine_value=changed_old).values_list('english_name', flat=True)
                                changed_new_qs = FieldChoice.objects.filter(
                                    machine_value=changed_new).values_list('english_name', flat=True)
                            else:
                                changed_old_qs = FieldChoice.objects.filter(
                                    pk__in=changed_old).values_list('english_name', flat=True)
                                changed_new_qs = FieldChoice.objects.filter(
                                    pk__in=changed_new).values_list('english_name', flat=True)
                            changed_old = ', '.join(list(changed_old_qs))
                            changed_new = ', '.join(list(changed_new_qs))

                        if changed_old in ('', None):
                            changed_old = '-'
                        if changed_new in ('', None):
                            changed_new = '-'

                        revisions.append((version_hist_entry.revision.user.username, version_hist_entry.revision.date_created,
                                          changed_field_verbosename, changed_old, changed_new))

                # Translations
                translations_new = list(version_history[i].revision.version_set.filter(
                    content_type=translation_contenttype).values_list('object_repr', flat=True))
                translations_old = list(version_history[i+1].revision.version_set.filter(
                    content_type=translation_contenttype).values_list('object_repr', flat=True))

                # Ignore pairs of empty lists
                if not (translations_new or translations_old):
                    continue

                # This will catch re-orderings as well
                translations_new_str = ", ".join(translations_new)
                translations_old_str = ", ".join(translations_old)
                if (translations_new_str != translations_old_str):
                    revisions.append((version_hist_entry.revision.user.username, version_hist_entry.revision.date_created,
                                      'Translations', translations_old_str, translations_new_str))

            context['revisions'] = revisions

        # Pass info about which fields we want to see
        gl = context['gloss']
        labels = gl.field_labels()

        fields = dict()

        fields['morphology'] = ['number_incorporated', 'locatable', 'directional', 'fingerspelling',
                                'inflection_temporal', 'inflection_manner_degree', 'inflection_plural']
        fields['phonology'] = ['handedness', 'strong_handshape', 'weak_handshape', 'handshape_change',
                               'relation_between_articulators', 'location', 'contact_type',
                               'repeated_movement', 'alternating_movement',
                               'mouth_gesture', 'mouthing', 'phonetic_variation', 'one_or_two_hand']

        fields['semantics'] = ['iconic_image',
                               'named_entity']
        fields['usage'] = ['variant_no']
        fields['examples'] = ['videoexample1', 'videoexample1_translation', 'videoexample2', 'videoexample2_translation',
                              'videoexample3', 'videoexample3_translation', 'videoexample4', 'videoexample4_translation']

        fields['frequency'] = ['number_of_occurences']

        for topic in ['morphology', 'phonology', 'semantics', 'frequency', 'examples', 'usage']:
            context[topic + '_fields'] = []

            for field in fields[topic]:

                try:
                    value = getattr(gl, 'get_' + field + '_display')
                except AttributeError:
                    value = getattr(gl, field)

                if field in ['phonology_other', 'mouth_gesture', 'mouthing', 'phonetic_variation', 'iconic_image']:
                    kind = 'text'
                elif field in ['repeated_movement', 'alternating_movement', 'fingerspelling', 'one_or_two_hand', 'number_incorporated', 'locatable', 'directional', 'inflection_temporal', 'inflection_manner_degree', 'inflection_plural']:
                    kind = 'check'
                else:
                    kind = 'list'

                context[topic +
                        '_fields'].append([value, field, labels[field], kind])

        return context


def gloss_ajax_search_results(request):
    """Returns a JSON list of glosses that match the previous search stored in sessions"""
    if 'search_results' in request.session and request.session['search_results'] != '':
        return JsonResponse(request.session['search_results'], safe=False)
    else:
        return HttpResponse("OK", status=200)


def gloss_ajax_complete(request, prefix):
    """Return a list of glosses matching the search term as a JSON structure suitable for typeahead."""

    query = Q(idgloss__istartswith=prefix)
    qs = Gloss.objects.filter(query)

    result = []

    for g in qs:
        result.append(
            {'idgloss': g.idgloss, 'pk': "%s (%s)" % (g.idgloss, g.pk)})

    return HttpResponse(json.dumps(result), {'content-type': 'application/json'})


def gloss_list_xml(self, dataset_id):
    """Returns all entries in dictionarys idgloss fields in XML form that is supported by ELAN"""
    # http://www.mpi.nl/tools/elan/EAFv2.8.xsd
    dataset = get_object_or_404(Dataset, id=dataset_id)
    return serialize_glosses(dataset,
                             Gloss.objects.filter(
                                 dataset=dataset, exclude_from_ecv=False)
                             .prefetch_related(
                                 Prefetch('translation_set', queryset=Translation.objects.filter(gloss__dataset=dataset)
                                          .select_related('keyword', 'language')),
                                 Prefetch('glosstranslations_set', queryset=GlossTranslations.objects.
                                          filter(gloss__dataset=dataset).select_related('language'))))


def serialize_glosses(dataset, queryset):
    for gloss in queryset:
        # Get Finnish translation equivalents from glosstranslations or from translation_set
        if gloss.glosstranslations_set.exists() and "fin" in [x.language.language_code_3char for x in
                                                              gloss.glosstranslations_set.all()]:
            gloss.trans_fin = [x for x in gloss.glosstranslations_set.all(
            ) if x.language.language_code_3char == "fin"]
        else:
            gloss.trans_fin = [x.keyword.text for x in gloss.translation_set.all() if
                               x.language.language_code_3char == "fin"]
        # Get English translation equivalents from glosstranslations or from translation_set
        if gloss.glosstranslations_set.exists() and "eng" in [x.language.language_code_3char for x in
                                                              gloss.glosstranslations_set.all()]:
            gloss.trans_eng = [x for x in gloss.glosstranslations_set.all() if
                               x.language.language_code_3char == "eng"]
        else:
            gloss.trans_eng = [x.keyword.text for x in gloss.translation_set.all() if
                               x.language.language_code_3char == "eng"]

    xml = render_to_string('dictionary/xml_glosslist_template.xml',
                           {'queryset': queryset, 'dataset': dataset})
    return HttpResponse(xml, content_type="text/xml")


def gloss_list_csv(self, dataset_id):
    """Returns glosses and associated data as a CSV file"""
    dataset = get_object_or_404(Dataset, id=dataset_id)
    return serialize_glosses_csv(dataset,
                                 Gloss.objects.filter(
                                     dataset=dataset, exclude_from_ecv=False)
                                 .prefetch_related(
                                     Prefetch('translation_set', queryset=Translation.objects.filter(gloss__dataset=dataset)
                                              .select_related('keyword', 'language')),
                                     Prefetch('glosstranslations_set', queryset=GlossTranslations.objects.
                                              filter(gloss__dataset=dataset).select_related('language'))))


def serialize_glosses_csv(dataset, queryset):
    return djqscsv.render_to_csv_response(queryset)


class GlossRelationListView(ListView):
    model = GlossRelation
    template_name = 'dictionary/admin_glossrelation_list.html'
    paginate_by = 100

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(GlossRelationListView, self).get_context_data(**kwargs)
        context['searchform'] = GlossRelationSearchForm(self.request.GET)
        # Get allowed datasets for user (django-guardian)
        allowed_datasets = get_objects_for_user(
            self.request.user, 'dictionary.view_dataset')
        # Filter the forms dataset field for the datasets user has permission to.
        context['searchform'].fields["dataset"].queryset = Dataset.objects.filter(
            id__in=[x.id for x in allowed_datasets])

        populate_tags_for_object_list(
            context['object_list'], model=self.object_list.model)

        if 'order' not in self.request.GET:
            context['order'] = 'source'
        else:
            context['order'] = self.request.GET.get('order')

        return context

    def get_paginate_by(self, queryset):
        """
        Paginate by specified value in querystring, or use default class property value.
        """
        return self.request.GET.get('paginate_by', self.paginate_by)

    def get_queryset(self):
        # get query terms from self.request
        qs = GlossRelation.objects.all()

        # Filter in only objects in the datasets the user has permissions to.
        allowed_datasets = get_objects_for_user(
            self.request.user, 'dictionary.view_dataset')
        qs = qs.filter(source__dataset__in=allowed_datasets).filter(
            target__dataset__in=allowed_datasets)

        get = self.request.GET

        # Search for multiple datasets (if provided)
        vals = get.getlist('dataset', [])
        if vals != []:
            qs = qs.filter(source__dataset__in=vals).filter(
                target__dataset__in=vals)

        if 'search' in get and get['search'] != '':
            val = get['search']
            # Searches for multiple fields at the same time. Looking if any of the fields match.
            query = (Q(source__idgloss__icontains=val) |
                     Q(target__idgloss__icontains=val))
            qs = qs.filter(query)

        if 'source' in get and get['source'] != '':
            val = get['source']
            # Search for sources glosses starting with a string, case sensitive
            query = Q(source__idgloss__istartswith=val)
            qs = qs.filter(query)

        if 'target' in get and get['target'] != '':
            val = get['target']
            # Search for sources glosses starting with a string, case sensitive
            query = Q(target__idgloss__istartswith=val)
            qs = qs.filter(query)

        if 'tags' in get and get['tags'] != '':
            vals = get.getlist('tags', [])
            tags = []
            for t in vals:
                tags.extend(Tag.objects.filter(pk=t))

            # search is an implicit AND so intersection
            tqs = TaggedItem.objects.get_intersection_by_model(GlossRelation, tags)

            # intersection
            qs = qs & tqs

        # Prefetching translation and dataset objects for glosses to minimize the amount of database queries.
        qs = qs.prefetch_related(Prefetch('source__dataset'), Prefetch('target__dataset'),
                                 Prefetch('source__glossvideo_set', queryset=GlossVideo.objects.all().order_by(
                                     'version')),
                                 Prefetch(
                                     'target__glossvideo_set', queryset=GlossVideo.objects.all().order_by('version'))
                                 )

        # Set order according to GET field 'order'
        if 'order' in get:
            qs = qs.order_by(get['order'])
        else:
            qs = qs.order_by('id')
        return qs
