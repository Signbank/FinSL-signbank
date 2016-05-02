import csv

from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.db.models import Q
from django.db.models.fields import NullBooleanField
from django.http import HttpResponse
from django.core.exceptions import PermissionDenied
from tagging.models import Tag, TaggedItem
from django.template.loader import render_to_string
from django.http import JsonResponse

from signbank.dictionary.forms import *
from signbank.feedback.forms import *
from signbank.video.forms import VideoUploadForGlossForm


class GlossListView(ListView):
    model = Gloss
    template_name = 'dictionary/admin_gloss_list.html'
    paginate_by = 100

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(GlossListView, self).get_context_data(**kwargs)
        # Add in a QuerySet
        context['searchform'] = GlossSearchForm(self.request.GET)
        context['glosscount'] = Gloss.objects.all().count()
        context['ADMIN_RESULT_FIELDS'] = settings.ADMIN_RESULT_FIELDS
        if not self.request.GET.has_key('order'):
            context['order'] = 'idgloss'
        else:
            context['order'] = self.request.GET.get('order')
        return context

    def get_paginate_by(self, queryset):
        """
        Paginate by specified value in querystring, or use default class property value.
        """
        return self.request.GET.get('paginate_by', self.paginate_by)

    def render_to_response(self, context):
        # Look for a 'format=json' GET argument
        if self.request.GET.get('format') == 'CSV':
            return self.render_to_csv_response(context)
        else:
            return super(GlossListView, self).render_to_response(context)

    # noinspection PyInterpreter,PyInterpreter
    def render_to_csv_response(self, context):

        if not self.request.user.has_perm('dictionary.export_csv'):
            raise PermissionDenied

        # Create the HttpResponse object with the appropriate CSV header.
        response = HttpResponse(content_type='text/csv')
        response[
            'Content-Disposition'] = 'attachment; filename="dictionary-export.csv"'


        #        fields = [f.name for f in Gloss._meta.fields]
        # We want to manually set which fields to export here

        fieldnames = ['idgloss', 'idgloss_en', 'annotation_comments', 'handedness', 'strong_handshape',
                      'weak_handshape', 'handshape_change', 'relation_between_articulators', 'location',
                      'absolute_orientation_palm', 'absolute_orientation_fingers', 'relative_orientation_movement',
                      'relative_orientation_location', 'orientation_change', 'contact_type',
                      'movement_shape', 'movement_direction', 'movement_manner', 'repeated_movement',
                      'alternating_movement', 'phonology_other', 'mouth_gesture', 'mouthing', 'phonetic_variation',
                      'iconic_image', 'named_entity', 'semantic_field', 'number_of_occurences',
                      'in_web_dictionary', 'is_proposed_new_sign']
        fields = [Gloss._meta.get_field(fieldname) for fieldname in fieldnames]

        writer = csv.writer(response)

        # Defines the headings for the file. Signbank ID and Dataset are set first.
        header = ['Signbank ID'] + ['Dataset'] + [f.verbose_name for f in fields]

        for extra_column in ['Language', 'Dialects', 'Keywords', 'Morphology', 'Relations to other signs',
                             'Relations to foreign signs', ]:
            header.append(extra_column)

        writer.writerow(header)

        for gloss in self.get_queryset():
            row = [unicode(gloss.pk)]
            # Adding Dataset information for the gloss
            row.append(unicode(gloss.dataset))
            for f in fields:

                # Try the value of the choicelist
                try:
                    row.append(getattr(gloss, 'get_' + f.name + '_display')())

                # If it's not there, try the raw value
                except AttributeError:
                    value = getattr(gloss, f.name)

                    if isinstance(value, unicode):
                        value = unicode(value)
                    elif not isinstance(value, str):
                        value = unicode(value)

                    row.append(value)

            # get language, adding only one language. Used to add several but requirement changed.
            language = gloss.dataset.language
            row.append(unicode(language))

            # get dialects
            dialects = [dialect.name for dialect in gloss.dialect.all()]
            row.append(", ".join(dialects))

            # get translations
            trans = [t.translation.text for t in gloss.translation_set.all()]
            row.append(", ".join(trans))

            # get morphology
            morphemes = [unicode(morpheme) for morpheme in MorphologyDefinition.objects.filter(
                parent_gloss=gloss)]
            row.append(", ".join(morphemes))

            # get relations to other signs
            relations = [
                relation.target.idgloss for relation in Relation.objects.filter(source=gloss)]
            row.append(", ".join(relations))

            # get relations to foreign signs
            relations = [
                relation.other_lang_gloss for relation in RelationToForeignSign.objects.filter(gloss=gloss)]
            row.append(", ".join(relations))

            # Make it safe for weird chars
            safe_row = []
            for column in row:
                try:
                    safe_row.append(column.encode('utf-8'))
                except AttributeError:
                    safe_row.append(None)

            writer.writerow(safe_row)

        return response

    def get_queryset(self):

        # get query terms from self.request
        qs = Gloss.objects.all()

        get = self.request.GET

        # Search for multiple datasets (if provided)
        vals = get.getlist('dataset', [])
        if vals != []:
            qs = qs.filter(dataset__in=vals)

        if get.has_key('search') and get['search'] != '':
            val = get['search']

            # Add fields you want to search logically with GET.search using | (OR) and & (AND)
            # Search for glosses containing a string, casesensitive with icontains
            query = Q(idgloss__icontains=val)

            qs = qs.filter(query)

        if get.has_key('idgloss_en') and get['idgloss_en'] != '':
            val = get['idgloss_en']
            qs = qs.filter(idgloss_en__icontains=val)

        if get.has_key('keyword') and get['keyword'] != '':
            val = get['keyword']
            qs = qs.filter(translation__translation__text__icontains=val)

        if get.has_key('keyword_eng') and get['keyword_eng'] != '':
            val = get['keyword_eng']
            qs = qs.filter(translationenglish__translation_english__text__icontains=val)

        if get.has_key('in_web_dictionary') and get['in_web_dictionary'] != 'unspecified':
            val = get['in_web_dictionary'] == 'yes'
            qs = qs.filter(in_web_dictionary__exact=val)
            # print "B :", len(qs)

        if get.has_key('hasvideo') and get['hasvideo'] != 'unspecified':
            val = get['hasvideo'] == 'no'

            qs = qs.filter(glossvideo__isnull=val)

        if get.has_key('defspublished') and get['defspublished'] != 'unspecified':
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

        if get.has_key('annotation_comments') and get['annotation_comments'] != '':
            qs = qs.filter(annotation_comments__icontains=get['annotation_comments'])

        # phonology and semantics field filters
        for fieldname in fieldnames:

            if get.has_key(fieldname):
                key = fieldname + '__exact'
                val = get[fieldname]

                if isinstance(Gloss._meta.get_field(fieldname), NullBooleanField):
                    val = {'0': '', '1': None, '2': True, '3': False}[val]

                if val != '':
                    kwargs = {key: val}
                    qs = qs.filter(**kwargs)

        if get.has_key('defsearch') and get['defsearch'] != '':

            val = get['defsearch']

            if get.has_key('defrole'):
                role = get['defrole']
            else:
                role = 'all'

            if role == 'all':
                qs = qs.filter(definition__text__icontains=val)
            else:
                qs = qs.filter(
                    definition__text__icontains=val, definition__role__exact=role)

        if get.has_key('tags') and get['tags'] != '':
            vals = get.getlist('tags')

            tags = []
            for t in vals:
                tags.extend(Tag.objects.filter(name=t))

            # search is an implicit AND so intersection
            tqs = TaggedItem.objects.get_intersection_by_model(Gloss, tags)

            # intersection
            qs = qs & tqs

            # print "J :", len(qs)

        qs = qs.distinct()

        if get.has_key('nottags') and get['nottags'] != '':
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

        if get.has_key('relationToForeignSign') and get['relationToForeignSign'] != '':
            relations = RelationToForeignSign.objects.filter(
                other_lang_gloss__icontains=get['relationToForeignSign'])
            potential_pks = [relation.gloss.pk for relation in relations]
            qs = qs.filter(pk__in=potential_pks)

        if get.has_key('hasRelationToForeignSign') and get['hasRelationToForeignSign'] != '0':

            pks_for_glosses_with_relations = [
                relation.gloss.pk for relation in RelationToForeignSign.objects.all()]
            print('pks_for_glosses', pks_for_glosses_with_relations)

            # We only want glosses with a relation to a foreign sign
            if get['hasRelationToForeignSign'] == '1':
                qs = qs.filter(pk__in=pks_for_glosses_with_relations)
            # We only want glosses without a relation to a foreign sign
            elif get['hasRelationToForeignSign'] == '2':
                qs = qs.exclude(pk__in=pks_for_glosses_with_relations)

        if get.has_key('relation') and get['relation'] != '':
            potential_targets = Gloss.objects.filter(
                idgloss__icontains=get['relation'])
            relations = Relation.objects.filter(target__in=potential_targets)
            potential_pks = [relation.source.pk for relation in relations]
            qs = qs.filter(pk__in=potential_pks)

        if get.has_key('hasRelation') and get['hasRelation'] != '':

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

        if get.has_key('morpheme') and get['morpheme'] != '':
            potential_morphemes = Gloss.objects.filter(
                idgloss__icontains=get['morpheme'])
            potential_morphdefs = MorphologyDefinition.objects.filter(
                morpheme__in=[morpheme.pk for morpheme in potential_morphemes])
            potential_pks = [
                morphdef.parent_gloss.pk for morphdef in potential_morphdefs]
            qs = qs.filter(pk__in=potential_pks)

        if get.has_key('hasMorphemeOfType') and get['hasMorphemeOfType'] != '':
            morphdefs_with_correct_role = MorphologyDefinition.objects.filter(
                role__exact=get['hasMorphemeOfType'])
            pks_for_glosses_with_morphdefs_with_correct_role = [
                morphdef.parent_gloss.pk for morphdef in morphdefs_with_correct_role]
            qs = qs.filter(
                pk__in=pks_for_glosses_with_morphdefs_with_correct_role)

        if get.has_key('definitionRole') and get['definitionRole'] != '':

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

        if get.has_key('definitionContains') and get['definitionContains'] != '':
            definitions_with_this_text = Definition.objects.filter(
                text__icontains=get['definitionContains'])

            # Remember the pk of all glosses that are referenced in the
            # collection definitions
            pks_for_glosses_with_these_definitions = [
                definition.gloss.pk for definition in definitions_with_this_text]
            qs = qs.filter(pk__in=pks_for_glosses_with_these_definitions)

            # print "Final :", len(qs)

        # Set order according to GET field 'order'
        if get.has_key('order'):
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
                items.append(dict(id = item.id, gloss = item.idgloss))

            self.request.session['search_results'] = items

        return qs


class GlossDetailView(DetailView):
    model = Gloss
    context_object_name = 'gloss'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(GlossDetailView, self).get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        context['tagform'] = TagUpdateForm()
        context['videoform'] = VideoUploadForGlossForm()
        context['definitionform'] = DefinitionForm()
        context['relationform'] = RelationForm()
        context['morphologyform'] = MorphologyForm()
        context['interpform'] = InterpreterFeedbackForm()

        # Pass info about which fields we want to see
        gl = context['gloss']
        labels = gl.field_labels()

        fields = {}

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

    return JsonResponse(request.session['search_results'], safe=False)

def gloss_ajax_complete(request, prefix):
    """Return a list of glosses matching the search term as a JSON structure suitable for typeahead."""

    query = Q(idgloss__istartswith=prefix)
    qs = Gloss.objects.filter(query)

    result = []

    for g in qs:
        result.append({'idgloss': g.idgloss, 'pk': "%s (%s)" % (g.idgloss, g.pk)})

    return HttpResponse(json.dumps(result), {'content-type': 'application/json'})

def gloss_list_xml(self):
    """Returns all entries in dictionarys idgloss fields in XML form that is supported by ELAN"""
    # http://www.mpi.nl/tools/elan/EAFv2.8.xsd
    return my_serialize(Gloss.objects.all())

def my_serialize(query_set):
    xml = render_to_string('dictionary/xml_glosslist_template.xml', {'query_set': query_set})
    return HttpResponse(xml, content_type="text/xml")

