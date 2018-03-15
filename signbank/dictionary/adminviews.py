# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
import csv
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.db.models import Q, Count
from django.db.models.fields import NullBooleanField
from django.http import HttpResponse, JsonResponse
from django.core.exceptions import PermissionDenied
from django.template.loader import render_to_string
from django.utils.translation import get_language
from django.db.models import Prefetch
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext as _

from collections import defaultdict
from django.contrib import messages
from tagging.models import Tag, TaggedItem
from guardian.shortcuts import get_perms, get_objects_for_user, get_users_with_perms
from reversion.models import Version

from .forms import GlossSearchForm, TagsAddForm, GlossRelationForm, RelationForm, MorphologyForm, \
    GlossRelationSearchForm
from .models import Gloss, Dataset, Translation, GlossTranslations, GlossURL, GlossRelation, RelationToForeignSign, \
    Relation, MorphologyDefinition
from ..video.forms import VideoUploadForGlossForm
from ..video.models import GlossVideo
from ..comments import CommentTagForm


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
        allowed_datasets = get_objects_for_user(self.request.user, 'dictionary.view_dataset')
        # Filter the forms dataset field for the datasets user has permission to.
        context['searchform'].fields["dataset"].queryset = Dataset.objects.filter(id__in=[x.id for x in allowed_datasets])

        populate_tags_for_object_list(context['object_list'], model=self.object_list.model)

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
        if self.request.GET.get('format') == 'CSV':
            return self.render_to_csv_response(context)
        else:
            return super(GlossListView, self).render_to_response(context)

    # noinspection PyInterpreter,PyInterpreter
    def render_to_csv_response(self, context):

        if not self.request.user.has_perm('dictionary.export_csv'):
            msg = _("You do not have permissions to export to CSV.")
            messages.error(self.request, msg)
            raise PermissionDenied(msg)

        # Create the HttpResponse object with the appropriate CSV header.
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename="dictionary-export.csv"'

        writer = csv.writer(response)

        csv_queryset = self.get_queryset()\
            .select_related('created_by', 'updated_by')\
            .prefetch_related('translation_set', 'glosstranslations_set')

        # We want to manually set which fields to export here
        fieldnames = ['idgloss', 'idgloss_en', 'notes', ]
        fields = [Gloss._meta.get_field(fieldname) for fieldname in fieldnames]

        # Defines the headings for the file. Signbank ID and Dataset are set first.
        header = ['Signbank ID'] + ['Dataset'] + [f.verbose_name for f in fields]

        for extra_column in ['SignLanguage', 'Keywords', 'Created', 'Updated']:
            header.append(extra_column)

        writer.writerow(header)

        for gloss in csv_queryset:
            row = list()
            row.append(str(gloss.pk))
            # Adding Dataset information for the gloss
            row.append(str(gloss.dataset))
            # Add data from each field.
            for f in fields:
                value = getattr(gloss, f.name)
                # If the value contains ';', put it in quotes.
                if ";" in value:
                    row.append('"{}"'.format(value))
                else:
                    row.append(value)

            # Get SignLanguage of Gloss
            signlanguage = gloss.dataset.signlanguage
            row.append(signlanguage)

            # Get Translation equivalents. If GlossTranslations don't exist, get Translations.
            if gloss.glosstranslations_set.all():
                trans = [t.translations for t in gloss.glosstranslations_set.all()]
            else:
                # Translations are shown per user selected interface language, related objects don't work in this case.
                trans = [t.keyword.text for t in Translation.objects.filter(gloss=gloss)]
            translations = ", ".join(trans)
            # Put translations inside quotes, because GlossTranslations might have ';'.
            row.append('"{}"'.format(translations))

            # Created at and by
            created = str(gloss.created_at)+' by: '+str(gloss.created_by)
            row.append(created)
            # Updated at and by
            updated = str(gloss.updated_at)+' by: '+str(gloss.updated_by)
            row.append(updated)

            writer.writerow(row)

        return response

    def get_queryset(self):
        # get query terms from self.request
        qs = Gloss.objects.all()

        # Filter in only objects in the datasets the user has permissions to.
        allowed_datasets = get_objects_for_user(self.request.user, 'dictionary.view_dataset')
        qs = qs.filter(dataset__in=allowed_datasets)

        get = self.request.GET

        # Search for multiple datasets (if provided)
        vals = get.getlist('dataset', [])
        if vals != []:
            qs = qs.filter(dataset__in=vals)

        if 'search' in get and get['search'] != '':
            val = get['search']
            # Searches for multiple fields at the same time. Looking if any of the fields match.
            query = (Q(idgloss__icontains=val) | Q(idgloss_en__icontains=val) | Q(notes__icontains=val) |
                     Q(translation__keyword__text__icontains=val))
            qs = qs.filter(query)

        if 'gloss' in get and get['gloss'] != '':
            val = get['gloss']
            # Search for glosses starting with a string, case sensitive
            query = Q(idgloss__istartswith=val)
            qs = qs.filter(query)

        if 'idgloss_en' in get and get['idgloss_en'] != '':
            val = get['idgloss_en']
            qs = qs.filter(idgloss_en__istartswith=val)
        if 'keyword' in get and get['keyword'] != '':
            if 'trans_lang' in get and get['trans_lang'] != '':
                val = get['keyword']
                lang = get['trans_lang']
                qs = qs.filter(translation__keyword__text__icontains=val, translation__language__in=lang)

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
            qs = qs.annotate(videocount=Count('glossvideo')).filter(videocount__gt=1)


        # A list of phonology fieldnames
        fieldnames = ['handedness', 'strong_handshape', 'weak_handshape', 'location', 'relation_between_articulators',
                      'absolute_orientation_palm', 'absolute_orientation_fingers', 'relative_orientation_movement',
                      'relative_orientation_location', 'orientation_change', 'handshape_change', 'repeated_movement',
                      'alternating_movement', 'movement_shape', 'movement_direction', 'movement_manner',
                      'contact_type', 'phonology_other', 'mouth_gesture', 'mouthing', 'phonetic_variation',
                      'iconic_image', 'named_entity', 'semantic_field', 'number_of_occurences', ]

        """These were removed from fieldnames because they are not needed there:
        'idgloss', 'idgloss_en', 'notes',
        """


        # Language and basic property filters
        vals = get.getlist('dialect', [])
        if vals != []:
            qs = qs.filter(dialect__in=vals)

        vals = get.getlist('language', [])
        if vals != []:
            # Get languages from dataset
            qs = qs.filter(dataset__language__in=vals)

        vals = get.getlist('signlanguage', [])
        if vals != []:
            # Get sign languages from dataset
            qs = qs.filter(dataset__signlanguage__in=vals)

        if 'notes' in get and get['notes'] != '':
            qs = qs.filter(notes__icontains=get['notes'])

        # phonology and semantics field filters
        for fieldname in fieldnames:

            if fieldname in get:
                key = fieldname + '__exact'
                val = get[fieldname]

                if isinstance(Gloss._meta.get_field(fieldname), NullBooleanField):
                    val = {'0': '', '1': None, '2': True, '3': False}[val]

                if val != '':
                    kwargs = {key: val}
                    qs = qs.filter(**kwargs)

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

        if 'relationToForeignSign' in get and get['relationToForeignSign'] != '':
            relations = RelationToForeignSign.objects.filter(
                other_lang_gloss__icontains=get['relationToForeignSign'])
            potential_pks = [relation.gloss.pk for relation in relations]
            qs = qs.filter(pk__in=potential_pks)

        if 'hasRelationToForeignSign' in get and get['hasRelationToForeignSign'] != '0':

            pks_for_glosses_with_relations = [
                relation.gloss.pk for relation in RelationToForeignSign.objects.all()]
            print(('pks_for_glosses', pks_for_glosses_with_relations))

            # We only want glosses with a relation to a foreign sign
            if get['hasRelationToForeignSign'] == '1':
                qs = qs.filter(pk__in=pks_for_glosses_with_relations)
            # We only want glosses without a relation to a foreign sign
            elif get['hasRelationToForeignSign'] == '2':
                qs = qs.exclude(pk__in=pks_for_glosses_with_relations)

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
        context['dataset'] = self.get_object().dataset
        context['dataset_users'] = [x.username for x in get_users_with_perms(context['dataset'])]
        context['tagsaddform'] = TagsAddForm()
        context['commenttagform'] = CommentTagForm()
        context['videoform'] = VideoUploadForGlossForm()
        context['relationform'] = RelationForm()
        context['morphologyform'] = MorphologyForm()
        context['glossrelationform'] = GlossRelationForm(initial={'source': context['gloss'].id,})
        # Choices for GlossRelationForm
        context['glossrelation_choices'] = Gloss.objects.filter(dataset=self.get_object().dataset)
        # GlossRelations for this gloss
        context['glossrelations'] = GlossRelation.objects.filter(source=context['gloss'])
        context['glossrelations_reverse'] = GlossRelation.objects.filter(target=context['gloss'])
        context['glossurls'] = GlossURL.objects.filter(gloss=context['gloss'])
        context['translation_languages_and_translations'] = \
            context['gloss'].get_translations_for_translation_languages()

        if self.request.user.is_staff:
            # Get some version history data
            version_history = Version.objects.get_for_object(context['gloss']).prefetch_related('revision__user')
            translation_ct = ContentType.objects.get_for_model(Translation)
            for i, version in enumerate(version_history):
                if not i+1 >= len(version_history):
                    ver1 = version.field_dict
                    ver2 = version_history[i+1].field_dict
                    t1 = [x.object_repr for x in version.revision.version_set.filter(content_type=translation_ct)]
                    t2 = [x.object_repr for x in version_history[i+1].revision.version_set.filter(content_type=translation_ct)]
                    version.translations_added = ", ".join(["+"+x for x in t1 if x not in set(t2)])
                    version.translations_removed = ", ".join(["-"+x for x in t2 if x not in set(t1)])
                    version.data_removed = dict([(key, value) for key, value in ver1.items() if value != ver2[key] and
                                               key != 'updated_at' and key != 'updated_by_id'])
                    version.data_added = dict([(key, value) for key, value in ver2.items() if value != ver1[key] and
                                                 key != 'updated_at' and key != 'updated_by_id'])

            context['revisions'] = version_history

        # Pass info about which fields we want to see
        gl = context['gloss']
        labels = gl.field_labels()

        fields = dict()

        fields['phonology'] = ['handedness', 'strong_handshape', 'weak_handshape', 'handshape_change',
                               'relation_between_articulators', 'location', 'absolute_orientation_palm',
                               'absolute_orientation_fingers', 'relative_orientation_movement',
                               'relative_orientation_location', 'orientation_change', 'contact_type', 'movement_shape',
                               'movement_direction', 'movement_manner', 'repeated_movement', 'alternating_movement',
                               'phonology_other', 'mouth_gesture', 'mouthing', 'phonetic_variation', ]

        fields['semantics'] = ['iconic_image', 'named_entity', 'semantic_field']

        fields['frequency'] = ['number_of_occurences']

        for topic in ['phonology', 'semantics', 'frequency']:
            context[topic + '_fields'] = []

            for field in fields[topic]:

                try:
                    value = getattr(gl, 'get_' + field + '_display')
                except AttributeError:
                    value = getattr(gl, field)

                if field in ['phonology_other', 'mouth_gesture', 'mouthing', 'phonetic_variation', 'iconic_image']:
                    kind = 'text'
                elif field in ['repeated_movement', 'alternating_movement']:
                    kind = 'check'
                else:
                    kind = 'list'

                context[
                    topic + '_fields'].append([value, field, labels[field], kind])

        return context


def gloss_ajax_search_results(request):
    """Returns a JSON list of glosses that match the previous search stored in sessions"""
    if 'search_results' in request.session and request.session['search_results'] != '':
        return JsonResponse(request.session['search_results'], safe=False)
    else:
        return HttpResponse("OK")


def gloss_ajax_complete(request, prefix):
    """Return a list of glosses matching the search term as a JSON structure suitable for typeahead."""

    query = Q(idgloss__istartswith=prefix)
    qs = Gloss.objects.filter(query)

    result = []

    for g in qs:
        result.append({'idgloss': g.idgloss, 'pk': "%s (%s)" % (g.idgloss, g.pk)})

    return HttpResponse(json.dumps(result), {'content-type': 'application/json'})


def gloss_list_xml(self, dataset):
    """Returns all entries in dictionarys idgloss fields in XML form that is supported by ELAN"""
    # http://www.mpi.nl/tools/elan/EAFv2.8.xsd
    dataset = Dataset.objects.get(id=dataset)
    return serialize_glosses(dataset,
                             Gloss.objects.filter(dataset=dataset)
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
            gloss.trans_fin = [x for x in gloss.glosstranslations_set.all() if x.language.language_code_3char=="fin"]
        else:
            gloss.trans_fin = [x.keyword.text for x in gloss.translation_set.all() if
                               x.language.language_code_3char == "fin"]
        # Get English translation equivalents from glosstranslations or from translation_set
        if gloss.glosstranslations_set.exists() and "eng" in [x.language.language_code_3char for x in
                                                              gloss.glosstranslations_set.all()]:
            gloss.trans_eng = [x for x in gloss.glosstranslations_set.all() if
                               x.language.language_code_3char=="eng"]
        else:
            gloss.trans_eng = [x.keyword.text for x in gloss.translation_set.all() if
                               x.language.language_code_3char == "eng"]

    xml = render_to_string('dictionary/xml_glosslist_template.xml', {'queryset': queryset, 'dataset': dataset})
    return HttpResponse(xml, content_type="text/xml")


class GlossRelationListView(ListView):
    model = GlossRelation
    template_name = 'dictionary/admin_glossrelation_list.html'
    paginate_by = 100

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(GlossRelationListView, self).get_context_data(**kwargs)
        context['searchform'] = GlossRelationSearchForm(self.request.GET)
        # Get allowed datasets for user (django-guardian)
        allowed_datasets = get_objects_for_user(self.request.user, 'dictionary.view_dataset')
        # Filter the forms dataset field for the datasets user has permission to.
        context['searchform'].fields["dataset"].queryset = Dataset.objects.filter(id__in=[x.id for x in allowed_datasets])

        populate_tags_for_object_list(context['object_list'], model=self.object_list.model)

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
        allowed_datasets = get_objects_for_user(self.request.user, 'dictionary.view_dataset')
        qs = qs.filter(source__dataset__in=allowed_datasets).filter(target__dataset__in=allowed_datasets)

        get = self.request.GET

        # Search for multiple datasets (if provided)
        vals = get.getlist('dataset', [])
        if vals != []:
            qs = qs.filter(source__dataset__in=vals).filter(target__dataset__in=vals)

        if 'search' in get and get['search'] != '':
            val = get['search']
            # Searches for multiple fields at the same time. Looking if any of the fields match.
            query = (Q(source__idgloss__icontains=val) | Q(target__idgloss__icontains=val))
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

        # Prefetching translation and dataset objects for glosses to minimize the amount of database queries.
        qs = qs.prefetch_related(Prefetch('source__dataset'), Prefetch('target__dataset'))

        # Set order according to GET field 'order'
        if 'order' in get:
            qs = qs.order_by(get['order'])
        else:
            qs = qs.order_by('source')
        return qs