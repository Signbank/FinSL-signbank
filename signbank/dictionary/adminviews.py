# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import django.utils.six as six
import json
import unicodecsv as csv
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.db.models import Q
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
from guardian.shortcuts import get_perms, get_objects_for_user

from .forms import GlossSearchForm, TagUpdateForm, GlossRelationForm, RelationForm, MorphologyForm, DefinitionForm
from .models import Gloss, Dataset, Translation, GlossTranslations, GlossURL, GlossRelation, RelationToForeignSign, \
    Relation, MorphologyDefinition, Definition
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

    def get_paginator(self, queryset, per_page, orphans=0, allow_empty_first_page=True, **kwargs):
        pag = self.paginator_class(queryset, per_page, orphans=orphans, allow_empty_first_page=allow_empty_first_page,
                                   **kwargs)
        # Putting character ranges in paginator
        paginate_char_ranges = list()
        for i in pag.page_range:
            page = pag.page(i)
            if not page.start_index() <= 0 or not page.end_index() <= 0:
                start_chars = pag.object_list[page.start_index() - 1].idgloss[:2].upper()
                end_chars = pag.object_list[page.end_index() - 1].idgloss[:2].upper()
                paginate_char_ranges.append(start_chars + "-" + end_chars)
        # Zip the range() of page_range and a list of character ranges.
        pag.paginate_ranges = list(zip(pag.page_range, paginate_char_ranges))
        if not len(paginate_char_ranges) <= 0:
            pag.paginate_last_range = paginate_char_ranges[len(paginate_char_ranges) - 1].upper()
        return pag

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
        response = HttpResponse(content_type='text/csv')
        response[
            'Content-Disposition'] = 'attachment; filename="dictionary-export.csv"'

        # We want to manually set which fields to export here
        fieldnames = ['idgloss', 'idgloss_en', 'annotation_comments', ]
        fields = [Gloss._meta.get_field(fieldname) for fieldname in fieldnames]

        writer = csv.writer(response)

        # Defines the headings for the file. Signbank ID and Dataset are set first.
        header = ['Signbank ID'] + ['Dataset'] + [f.verbose_name for f in fields]

        for extra_column in ['SignLanguage', 'Dialects', 'Keywords', 'Created', 'Updated']:
            header.append(extra_column)

        writer.writerow(header)

        for gloss in self.get_queryset():
            row = [str(gloss.pk)]
            # Adding Dataset information for the gloss
            row.append(str(gloss.dataset))
            for f in fields:

                # Try the value of the choicelist
                try:
                    row.append(getattr(gloss, 'get_' + f.name + '_display')())

                # If it's not there, try the raw value
                except AttributeError:
                    value = getattr(gloss, f.name)

                    if isinstance(value, six.text_type):
                        value = str(value)
                    elif not isinstance(value, bytes):
                        value = str(value)

                    row.append(value)

            # Get SignLanguage of Gloss
            signlanguage = gloss.dataset.signlanguage
            row.append(str(signlanguage))

            # get dialects
            dialects = [dialect.name for dialect in gloss.dialect.all()]
            row.append(", ".join(dialects))

            # get translations
            #trans = [t.keyword.text for t in gloss.translation_set.all()]
            # The search page lists only English translations, therefore we have to query for all of them.
            trans = [t.keyword.text for t in Translation.objects.filter(gloss=gloss)]
            row.append(", ".join(trans))

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
            query = (Q(idgloss__icontains=val) | Q(idgloss_en__icontains=val) | Q(annotation_comments__icontains=val) |
                     Q(translation__keyword__text__icontains=val))
            qs = qs.filter(query)

        if 'gloss' in get and get['gloss'] != '':
            val = get['gloss']

            # Add fields you want to search logically with GET.search using | (OR) and & (AND)
            # Search for glosses containing a string, casesensitive with icontains
            query = Q(idgloss__icontains=val)

            qs = qs.filter(query)

        if 'idgloss_en' in get and get['idgloss_en'] != '':
            val = get['idgloss_en']
            qs = qs.filter(idgloss_en__icontains=val)
        if 'keyword' in get and get['keyword'] != '':
            if 'trans_lang' in get and get['trans_lang'] != '':
                val = get['keyword']
                lang = get['trans_lang']
                qs = qs.filter(translation__keyword__text__icontains=val, translation__language__in=lang)

        if 'in_web_dictionary' in get and get['in_web_dictionary'] != 'unspecified':
            val = get['in_web_dictionary'] == 'yes'
            qs = qs.filter(in_web_dictionary__exact=val)
            # print "B :", len(qs)

        if 'islocked' in get and get['islocked'] != '':
            val = get['islocked'] == 'on'
            qs = qs.filter(locked=val)

        # If get has both keys hasvideo and hasnovideo, don't use them to query.
        if not ('hasvideo' in get and 'hasnovideo' in get):
            if 'hasvideo' in get and get['hasvideo'] != '':
                val = get['hasvideo'] != 'on'
                qs = qs.filter(glossvideo__isnull=val)

            if 'hasnovideo' in get and get['hasnovideo'] != '':
                val = get['hasnovideo'] == 'on'
                qs = qs.filter(glossvideo__isnull=val)

        if 'defspublished' in get and get['defspublished'] != 'unspecified':
            val = get['defspublished'] == 'yes'

            qs = qs.filter(definition__published=val)

        # A list of phonology fieldnames
        fieldnames = ['handedness', 'strong_handshape', 'weak_handshape', 'location', 'relation_between_articulators',
                      'absolute_orientation_palm', 'absolute_orientation_fingers', 'relative_orientation_movement',
                      'relative_orientation_location', 'orientation_change', 'handshape_change', 'repeated_movement',
                      'alternating_movement', 'movement_shape', 'movement_direction', 'movement_manner',
                      'contact_type', 'phonology_other', 'mouth_gesture', 'mouthing', 'phonetic_variation',
                      'iconic_image', 'named_entity', 'semantic_field', 'number_of_occurences',
                      'is_proposed_new_sign',]

        """These were removed from fieldnames because they are not needed there:
        'idgloss', 'idgloss_en', 'annotation_comments', 'in_web_dictionary',
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

        if 'annotation_comments' in get and get['annotation_comments'] != '':
            qs = qs.filter(annotation_comments__icontains=get['annotation_comments'])

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

        if 'defsearch' in get and get['defsearch'] != '':

            val = get['defsearch']

            if 'defrole' in get:
                role = get['defrole']
            else:
                role = 'all'

            if role == 'all':
                qs = qs.filter(definition__text__icontains=val)
            else:
                qs = qs.filter(
                    definition__text__icontains=val, definition__role__exact=role)

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

        if 'definitionRole' in get and get['definitionRole'] != '':

            # Find all definitions with this role
            if get['definitionRole'] == 'all':
                definitions_with_this_role = Definition.objects.all()
            else:
                definitions_with_this_role = Definition.objects.filter(
                    role__exact=get['definitionRole'])

            # Remember the pk of all glosses that are referenced in the
            # collection definitions
            pks_for_glosses_with_these_definitions = [
                definition.gloss.pk for definition in definitions_with_this_role]
            qs = qs.filter(pk__in=pks_for_glosses_with_these_definitions)

        if 'definitionContains' in get and get['definitionContains'] != '':
            definitions_with_this_text = Definition.objects.filter(
                text__icontains=get['definitionContains'])

            # Remember the pk of all glosses that are referenced in the
            # collection definitions
            pks_for_glosses_with_these_definitions = [
                definition.gloss.pk for definition in definitions_with_this_text]
            qs = qs.filter(pk__in=pks_for_glosses_with_these_definitions)

            # print "Final :", len(qs)

        # Set order according to GET field 'order'
        if 'order' in get:
            qs = qs.order_by(get['order'])
        else:
            qs = qs.order_by('idgloss')

        # Saving querysets results to sessions, these results can then be used elsewhere (like in gloss_detail)
        # Flush the previous queryset (just in case)
        self.request.session['search_results'] = None
        # Make sure that the QuerySet has filters applied (user is searching for something instead of showing all results [objects.all()])
        # TODO: Future me or future other developer, it could be useful to find a better way to do this, if one exists
        if hasattr(qs.query.where, 'children') and len(qs.query.where.children) > 0:
            items = []
            for item in qs:
                items.append(dict(id= item.id, gloss=item.idgloss))

            self.request.session['search_results'] = items

        # Prefetching translation and dataset objects for glosses to minimize the amount of database queries.
        qs = qs.prefetch_related(Prefetch('translation_set', queryset=Translation.objects.filter(
            language__language_code_2char__iexact=get_language()).select_related('keyword')),
                                 Prefetch('dataset'),
                                 # Ordering by version to get the first versions posterfile.
                                 Prefetch('glossvideo_set', queryset=GlossVideo.objects.all().order_by('version')))
        # Add tags for each Gloss in the queryset.
        populate_tags_for_queryset(qs)

        return qs


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
        context['tagform'] = TagUpdateForm()
        context['commenttagform'] = CommentTagForm()
        context['videoform'] = VideoUploadForGlossForm()
        context['definitionform'] = DefinitionForm()
        context['relationform'] = RelationForm()
        context['morphologyform'] = MorphologyForm()
        context['glossrelationform'] = GlossRelationForm(initial={'source': context['gloss'].id,})
        # Choices for GlossRelationForm
        context['glossrelation_choices'] = Gloss.objects.filter(dataset=self.get_object().dataset)
        # GlossRelations for this gloss
        context['glossrelations'] = GlossRelation.objects.filter(source=context['gloss'])
        context['glossurls'] = GlossURL.objects.filter(gloss=context['gloss'])
        context['translation_languages_and_translations'] = context['gloss'].get_translations_for_translation_languages()

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

