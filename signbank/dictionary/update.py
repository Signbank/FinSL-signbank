# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import re, csv
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden, HttpResponseBadRequest, Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.decorators import permission_required, login_required
from django.db.models.fields import NullBooleanField
from django.utils.translation import ugettext as _
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied

from tagging.models import TaggedItem
from guardian.shortcuts import get_perms, get_objects_for_user
from signbank.dictionary.models import *
from signbank.dictionary.forms import *
from signbank.video.views import addvideo
from ..video.models import GlossVideo


@permission_required('dictionary.add_gloss')
def add_gloss(request):
    # TODO: Is this view used anywhere?
    if request.method == 'POST':
        form = GlossCreateForm(request.POST, request.FILES)
        if form.is_valid():
            if 'view_dataset' not in get_perms(request.user, form.cleaned_data["dataset"]):
                # If user has no permissions to dataset, raise PermissionDenied to show 403 template.
                msg = _("You do not have permissions to create glosses for this lexicon.")
                messages.error(request, msg)
                raise PermissionDenied(msg)

            new_gloss = form.save(commit=False)
            new_gloss.created_by = request.user
            new_gloss.updated_by = request.user
            new_gloss.save()
            if form.cleaned_data["tag"]:
                Tag.objects.add_tag(new_gloss, form.cleaned_data["tag"].name)

            redirecturl = '/dictionary/gloss/' + str(new_gloss.pk) + '/?edit'
            addvideo(request, new_gloss.pk, redirecturl)
            #return HttpResponseRedirect(reverse('dictionary:admin_gloss_list'))
            return HttpResponseRedirect(redirecturl)
    else:
        form = GlossCreateForm()
        # Make sure that we will show the user only datasets the user is allowed access to.
        allowed_datasets = get_objects_for_user(request.user, 'dictionary.view_dataset')
        form.fields["dataset"].queryset = Dataset.objects.filter(id__in=[x.id for x in allowed_datasets])
    return render(request, 'dictionary/add_gloss.html', {'add_gloss_form': form})


@permission_required('dictionary.change_gloss')
def update_gloss(request, glossid):
    """View to update a gloss model from the jeditable jquery form
    We are sent one field and value at a time, return the new value once we've updated it."""

    # Make sure that the user has the rights to change a gloss
    if not request.user.has_perm('dictionary.change_gloss'):
        # Translators: HttpResponseForbidden for update_gloss
        return HttpResponseForbidden(_("Gloss Update Not Allowed"))

    # Get the gloss object or raise a Http404 exception if the object does not exist.
    gloss = get_object_or_404(Gloss, id=glossid)

    # Make sure that the user has rights to edit this datasets glosses.
    if 'view_dataset' not in get_perms(request.user, gloss.dataset):
        return HttpResponseForbidden(_("You do not have permissions to edit Glosses of this dataset/lexicon."))

    # If the Gloss object is locked, don't allow editing it.
    if gloss.locked:
        return HttpResponseForbidden(_("Gloss Update Not Allowed: Gloss is locked from editing"))

    if request.method == "POST":
        # Update the user on Gloss.updated_by from request.user
        gloss.updated_by = request.user
        old_idgloss = str(gloss)

        field = request.POST.get('id', '')
        value = request.POST.get('value', '')

        if len(value) == 0:
            value = ' '

        elif value[0] == '_':
            value = value[1:]

        # in case we need multiple values
        values = request.POST.getlist('value[]')

        # If field is 'deletegloss', delete the gloss and things related to it
        if field == 'deletegloss':
            if not request.user.has_perm('dictionary.delete_gloss'):
                # Translators: HttpResponseForbidden for deleting gloss without permission.
                return HttpResponseForbidden(_("You don't have permission to delete glosses."))
            if value == 'confirmed':
                # delete the gloss and redirect back to gloss list
                glosses_videos = GlossVideo.objects.filter(gloss=gloss)
                # Delete all the objects of GlossVideo that match the Gloss we try to delete.
                for video in glosses_videos: # TODO: Move this into video app
                    # When deleting the object, a signal is sent and catched at video.GlossVideo
                    # The signal handling will delete the videofile
                    video.delete()
                gloss.delete()
                return HttpResponseRedirect(reverse('admin_gloss_list'))

        if field.startswith('definition'):

            return update_definition(request, gloss, field, value)

        elif field.startswith('keywords_'):

            language_code_2char = field.split('_')[1]
            return update_keywords(gloss, field, value, language_code_2char=language_code_2char)

        elif field.startswith('relationforeign'):

            return update_relationtoforeignsign(gloss, field, value)

        # Had to add field != 'relation_between_articulators' because I changed its field name, and it conflicted here.
        elif field.startswith('relation') and field != 'relation_between_articulators':

            return update_relation(gloss, field, value)

        elif field.startswith('morphology-definition'):

            return update_morphology_definition(gloss, field, value)

        elif field == 'dialect':
            # expecting possibly multiple values
            try:
                gloss.dialect.clear()
                for value in values:
                    lang = Dialect.objects.get(name=value)
                    gloss.dialect.add(lang)
                gloss.save()
                newvalue = ", ".join([str(g.name)
                                      for g in gloss.dialect.all()])
            except:
                # Translators: HttpResponseBadRequest
                return HttpResponseBadRequest("%s %s" % _("Unknown Dialect"), values, content_type='text/plain')


        elif field == 'in_web_dictionary':
            # only modify if we have publish permission
            if request.user.has_perm('dictionary.can_publish'):
                gloss.in_web_dictionary = (value == 'Yes')
                gloss.save()

            if gloss.in_web_dictionary:
                newvalue = 'Yes'
            else:
                newvalue = 'No'

        elif field.startswith('video_title'):
            # If editing video title, update the GlossVideo's title
            if request.user.has_perm('video.change_glossvideo'):
                # Get pk after string "video_title"
                video_pk = field.split("video_title")[1]
                newvalue = value
                try:
                    video = GlossVideo.objects.get(pk=video_pk)
                    video.title = value
                    video.save()
                except GlossVideo.DoesNotExist:
                    pass

        elif field.startswith('glossurl-'):
            if field == 'glossurl-create':
                GlossURL.objects.create(url=value, gloss_id=glossid)
                return HttpResponseRedirect(reverse('dictionary:admin_gloss_view', kwargs={'pk': gloss.id}))
            else:
                if request.user.has_perm('dictionary.change_gloss'):
                    glossurl_pk = field.split('glossurl-')[1]
                    newvalue = value
                    try:
                        glossurl = GlossURL.objects.get(pk=glossurl_pk)
                        glossurl.url = value
                        glossurl.save()
                    except GlossURL.DoesNotExist:
                        pass

        else:
            # Find if field is not in Gloss classes fields.
            if not field in [f.name for f in Gloss._meta.get_fields()]:
                # Translators: HttpResponseBadRequest
                return HttpResponseBadRequest(_("Unknown field"), content_type='text/plain')

            # special cases
            # - Foreign Key fields (Language, Dialect)
            # - keywords
            # - videos
            # - tags

            # Translate the value if a boolean
            if isinstance(Gloss._meta.get_field(field), NullBooleanField):
                newvalue = value
                value = (value == 'Yes')

            # special value of 'notset' or -1 means remove the value
            if value == 'notset' or value == -1 or value == '':
                gloss.__setattr__(field, None)
                gloss.save()
                newvalue = ''
            else:
                # See if the field is a ForeignKey
                if gloss._meta.get_field(field).get_internal_type() == "ForeignKey":
                    gloss.__setattr__(field, FieldChoice.objects.get(machine_value=value))
                else:
                    gloss.__setattr__(field, value)
                gloss.save()

                # If the value is not a Boolean, return the new value
                if not isinstance(value, bool):

                    f = Gloss._meta.get_field(field)
                    # for choice fields we want to return the 'display' version of the value
                    # Try to use get_choices to get correct choice names for FieldChoices
                    # If it doesn't work, go to exception and get flatchoices
                    try:
                        # valdict = dict(f.get_choices(include_blank=False))
                        valdict = dict(build_choice_list(field))
                    except:
                        valdict = dict(f.flatchoices)

                    # Some fields take ints
                    # if valdict.keys() != [] and type(valdict.keys()[0]) == int:
                    try:
                        newvalue = valdict.get(int(value), value)
                    # else:
                    except:
                        # either it's not an int or there's no flatchoices
                        # so here we use get with a default of the value itself
                        newvalue = valdict.get(value, value)

            # If field is idgloss and if the value has changed
            # Then change the filename on system and in glossvideo.videofile
            if field == 'idgloss' and newvalue != old_idgloss:
                try:
                    GlossVideo.rename_glosses_videos(gloss)
                except (OSError, IOError):
                    # Catch error, but don't do anything for now.
                    pass

        return HttpResponse(newvalue, content_type='text/plain')


def update_keywords(gloss, field, value, language_code_2char):
    """Update the keyword field for the selected language"""

    # Try to get the language object based on the language_code.
    try:
        language = Language.objects.get(language_code_2char=language_code_2char)
    except Language.DoesNotExist:
        # If the language_code does not exist in any Language.language_code_2char, return 400 Bad Request.
        return HttpResponseBadRequest(_('A Language does not exist with language_code: ') + language_code_2char,
                                      content_type='text/plain')
    except Language.MultipleObjectsReturned:
        # If multiple Languages exist with the same language_code_2char
        return HttpResponseBadRequest(_('Multiple Languages with the same language_code exist, cannot edit because it '
                                        'is unclear which languages translations to edit.'),
                                      content_type='text/plain')

    # Removing instances of number(s) that end with a dot from the delivered 'value'.
    cleaned_value = re.sub('\d\.', '', value)
    # Splitting the remaining string on comma, dot or semicolon. Then strip spaces around the keyword(s).
    kwds = [k.strip() for k in re.split('[,.;]', cleaned_value)]
    # Remove current Translations
    current_trans = gloss.translation_set.filter(language=language)
    current_trans.delete()
    # Create new Translations, use existing Keywords if present or create new ones.
    for i in range(len(kwds)):
        (kobj, created) = Keyword.objects.get_or_create(text=kwds[i])
        # Create a new Translation, save the index to represent the order of Translations for this Gloss.
        trans = Translation(gloss=gloss, keyword=kobj, index=i, language=language)
        trans.save()

    try:
        glosstranslations = GlossTranslations.objects.get(gloss=gloss, language=language)
    except GlossTranslations.DoesNotExist:
        glosstranslations = GlossTranslations.objects.create(gloss=gloss, language=language)

    glosstranslations.translations = value
    glosstranslations.save()
    # Save updated_by field for Gloss
    gloss.save()
    return HttpResponse(value, content_type='text/plain')


def update_relation(gloss, field, value):
    """Update one of the relations for this gloss"""

    (what, relid) = field.split('_')
    what = what.replace('-', '_')

    try:
        rel = Relation.objects.get(id=relid)
    except Relation.DoesNotExist:
        # Translators: HttpResponseBadRequest
        return HttpResponseBadRequest("%s '%s'" % _("Bad Relation ID"), relid, content_type='text/plain')

    if not rel.source == gloss:
        # Translators: HttpResponseBadRequest
        return HttpResponseBadRequest(_("Relation doesn't match gloss"), content_type='text/plain')

    if what == 'relationdelete':
        print(("DELETE: ", rel))
        rel.delete()
        return HttpResponseRedirect(reverse('dictionary:admin_gloss_view', kwargs={'pk': gloss.id}))
    elif what == 'relationrole':
        #rel.role = value
        try:
            rel.role = FieldChoice.objects.get(machine_value=value)
        except FieldChoice.DoesNotExist:
            rel.role = value
        rel.save()
        #newvalue = rel.get_role_display()
        newvalue = rel.role
    elif what == 'relationtarget':

        target = gloss_from_identifier(value)
        if target:
            rel.target = target
            rel.save()
            newvalue = str(target)
        else:
            # Translators: HttpResponseBadRequest
            return HttpResponseBadRequest("%s '%s'" % _("Badly formed gloss identifier"), value,
                                          content_type='text/plain')
    else:
        # Translators: HttpResponseBadRequest
        return HttpResponseBadRequest("%s '%s'" % _("Unknown form field"), field, content_type='text/plain')

    return HttpResponse(newvalue, content_type='text/plain')


def update_relationtoforeignsign(gloss, field, value):
    """Update one of the relations for this gloss"""

    (what, relid) = field.split('_')
    what = what.replace('-', '_')

    try:
        rel = RelationToForeignSign.objects.get(id=relid)
    except RelationToForeignSign.DoesNotExist:
        # Translators: HttpResponseBadRequest
        return HttpResponseBadRequest("%s '%s'" % _("Bad RelationToForeignSign ID"), relid,
                                      content_type='text/plain')

    if not rel.gloss == gloss:
        # Translators: HttpResponseBadRequest
        return HttpResponseBadRequest(_("Relation doesn't match gloss"), content_type='text/plain')

    if what == 'relationforeigndelete':
        print(("DELETE: ", rel))
        rel.delete()
        return HttpResponseRedirect(reverse('dictionary:admin_gloss_view', kwargs={'pk': gloss.id}))
    elif what == 'relationforeign_loan':
        rel.loan = value == 'Yes'
        rel.save()

    elif what == 'relationforeign_other_lang':
        rel.other_lang = value
        rel.save()

    elif what == 'relationforeign_other_lang_gloss':
        rel.other_lang_gloss = value
        rel.save()

    else:
        # Translators: HttpResponseBadRequest
        return HttpResponseBadRequest("%s '%s'" % _("Unknown form field"), field, content_type='text/plain')

    return HttpResponse(value, content_type='text/plain')


def gloss_from_identifier(value):
    """Given an id of the form idgloss (pk) return the
    relevant gloss or None if none is found"""

    # We need another way to add a Relation to a Gloss. One textfield can't serve all the possible ways of adding.
    # One possible solution is to add two fields, one that serves adding by ID and other with Gloss name or name+id.
    # However, no one is going to memorize or check for the id numbers and they will probably add with Gloss name only.
    # Therefore the only useful implementation is to do it with the Gloss name only or with Glossname + id.
    # TODO: Decide what to do here

    """
    # See if 'value' is an int, should match if the user uses only an 'id' as a search string
    try:
        int(value)
        is_int = True
    except:
        is_int = False
    # If value is already int, try to match the int as IDGloss id.
    if is_int:
        try:
            target = Gloss.objects.get(pk=int(value))
        except ObjectDoesNotExist:
            # If the int doesn't match anything, return
            return HttpResponseBadRequest(_("Target gloss not found."), content_type='text/plain')

        return target
    # If 'value' is not int, then try to catch a string like "CAMEL (10)"
    else:"""

    # This regex looks from the Beginning of a string for IDGLOSS and then the id
    # For example: "CAMEL (10)", idgloss="CAMEL" and pk=10
    match = re.match('(.*) \((\d+)\)', value)

    if match:
        # print "MATCH: ", match
        idgloss = match.group(1)
        pk = match.group(2)
        # print "INFO: ", idgloss, pk
        # Try if target Gloss exists, if not, assign None to target, then it returns None
        try:
            target = Gloss.objects.get(pk=int(pk))
        except ObjectDoesNotExist:
            target = None
        # print "TARGET: ", target
        return target
    # If regex doesn't match, return None
    else:
        return None


def update_definition(request, gloss, field, value):
    """Update one of the definition fields"""

    (what, defid) = field.split('_')
    try:
        defn = Definition.objects.get(id=defid)
    except Definition.DoesNotExist:
        # Translators: HttpResponseBadRequest
        return HttpResponseBadRequest("%s '%s'" % _("Bad Definition ID"), defid, content_type='text/plain')

    if not defn.gloss == gloss:
        # Translators: HttpResponseBadRequest
        return HttpResponseBadRequest(_("Definition doesn't match gloss"), content_type='text/plain')

    if what == 'definitiondelete':
        defn.delete()
        return HttpResponseRedirect(reverse('dictionary:admin_gloss_view', kwargs={'pk': gloss.id}) + '?editdef')

    if what == 'definition':
        # update the definition
        defn.text = value
        defn.save()
        newvalue = defn.text
    elif what == 'definitioncount':
        defn.count = int(value)
        defn.save()
        newvalue = defn.count
    elif what == 'definitionpub':

        if request.user.has_perm('dictionary.can_publish'):
            defn.published = value == 'Yes'
            defn.save()

        if defn.published:
            newvalue = 'Yes'
        else:
            newvalue = 'No'
    elif what == 'definitionrole':
        defn.role = value
        defn.save()
        newvalue = defn.get_role_display()

    return HttpResponse(newvalue, content_type='text/plain')


def add_relation(request):
    """Add a new relation instance"""

    if request.method == "POST":

        form = RelationForm(request.POST)

        if form.is_valid():

            role = form.cleaned_data['role']
            sourceid = form.cleaned_data['sourceid']
            targetid = form.cleaned_data['targetid']

            try:
                source = Gloss.objects.get(pk=int(sourceid))
            except Gloss.DoesNotExist:
                # Translators: HttpResponseBadRequest
                return HttpResponseBadRequest(_("Source gloss not found."), content_type='text/plain')

            target = gloss_from_identifier(targetid)

            if target:
                rel = Relation(source=source, target=target, role=role)
                rel.save()

                return HttpResponseRedirect(
                    reverse('dictionary:admin_gloss_view', kwargs={'pk': source.id}) + '?editrel')
            else:
                # Translators: HttpResponseBadRequest
                return HttpResponseBadRequest(_("Target gloss not found."), content_type='text/plain')
        else:
            print(form)

    # fallback to redirecting to the requesting page
    return HttpResponseRedirect('/')


def add_relationtoforeignsign(request):
    """Add a new relationtoforeignsign instance"""

    if request.method == "POST":

        form = RelationToForeignSignForm(request.POST)

        if form.is_valid():

            sourceid = form.cleaned_data['sourceid']
            loan = form.cleaned_data['loan']
            other_lang = form.cleaned_data['other_lang']
            other_lang_gloss = form.cleaned_data['other_lang_gloss']

            try:
                gloss = Gloss.objects.get(pk=int(sourceid))
            except Gloss.DoesNotExist:
                # Translators: HttpResponseBadRequest
                return HttpResponseBadRequest(_("Source gloss not found."), content_type='text/plain')

            rel = RelationToForeignSign(gloss=gloss, loan=loan, other_lang=other_lang,
                                        other_lang_gloss=other_lang_gloss)
            rel.save()

            return HttpResponseRedirect(
                reverse('dictionary:admin_gloss_view', kwargs={'pk': gloss.id}) + '?editrelforeign')

        else:
            print(form)
            # Translators: HttpResponseBadRequest
            return HttpResponseBadRequest(_("Form not valid"), content_type='text/plain')

    # fallback to redirecting to the requesting page
    return HttpResponseRedirect('/')


def add_definition(request, glossid):
    """Add a new definition for this gloss"""

    thisgloss = get_object_or_404(Gloss, id=glossid)

    if request.method == "POST":
        form = DefinitionForm(request.POST)

        if form.is_valid():
            published = form.cleaned_data['published']
            count = form.cleaned_data['count']
            role = form.cleaned_data['role']
            text = form.cleaned_data['text']

            # create definition, default to not published
            defn = Definition(
                gloss=thisgloss, count=count, role=role, text=text, published=published)
            defn.save()

    return HttpResponseRedirect(reverse('dictionary:admin_gloss_view', kwargs={'pk': thisgloss.id}) + '?editdef')


def add_morphology_definition(request):
    if request.method == "POST":
        form = MorphologyForm(request.POST)

        if form.is_valid():
            parent_gloss = form.cleaned_data['parent_gloss_id']
            role = form.cleaned_data['role']
            morpheme_id = form.cleaned_data['morpheme_id']
            morpheme = gloss_from_identifier(morpheme_id)

            thisgloss = get_object_or_404(Gloss, pk=parent_gloss)

            # create definition, default to not published
            morphdef = MorphologyDefinition(
                parent_gloss=thisgloss, role=role, morpheme=morpheme)
            morphdef.save()

            return HttpResponseRedirect(
                reverse('dictionary:admin_gloss_view', kwargs={'pk': thisgloss.id}) + '?editmorphdef')
    # Translators: Htt404
    raise Http404(_('Incorrect request'))


def update_morphology_definition(gloss, field, value):
    """Update one of the relations for this gloss"""

    (what, morph_def_id) = field.split('_')
    what = what.replace('-', '_')

    try:
        morph_def = MorphologyDefinition.objects.get(id=morph_def_id)
    except MorphologyDefinition.DoesNotExist:
        # Translators: HttpResponseBadRequest
        return HttpResponseBadRequest("%s '%s'" % _("Bad Morphology Definition ID"), morph_def_id,
                                      content_type='text/plain')

    if not morph_def.parent_gloss == gloss:
        # Translators: HttpResponseBadRequest
        return HttpResponseBadRequest(_("Morphology Definition doesn't match gloss"), content_type='text/plain')

    if what == 'morphology_definition_delete':
        print(("DELETE: ", morph_def))
        morph_def.delete()
        return HttpResponseRedirect(reverse('dictionary:admin_gloss_view', kwargs={'pk': gloss.id}))
    elif what == 'morphology_definition_role':
        # morph_def.role = value
        morph_def.role = FieldChoice.objects.get(machine_value=value)
        morph_def.save()
        # newvalue = morph_def.get_role_display()
        newvalue = morph_def.role.english_name
    elif what == 'morphology_definition_morpheme':

        morpheme = gloss_from_identifier(value)
        if morpheme:
            morph_def.morpheme = morpheme
            morph_def.save()
            newvalue = str(morpheme)
        else:
            # Translators: HttpResponseBadRequest
            return HttpResponseBadRequest("%s '%s'" % _("Badly formed gloss identifier"), value,
                                          content_type='text/plain')
    else:
        # Translators: HttpResponseBadRequest
        return HttpResponseBadRequest("%s '%s'" % _("Unknown form field"), field, content_type='text/plain')

    return HttpResponse(newvalue, content_type='text/plain')


@permission_required('dictionary.change_gloss')
def add_tag(request, glossid):
    """View to add a tag to a gloss"""

    # default response
    response = HttpResponse('invalid', content_type='text/plain')

    if request.method == "POST":
        thisgloss = get_object_or_404(Gloss, id=glossid)
        if 'view_dataset' not in get_perms(request.user, thisgloss.dataset):
            # If user has no permissions to dataset, raise PermissionDenied to show 403 template.
            msg = _("You do not have permissions to add tags to glosses of this lexicon.")
            messages.error(request, msg)
            raise PermissionDenied(msg)

        form = TagUpdateForm(request.POST)
        if form.is_valid():

            tag = form.cleaned_data['tag']

            if form.cleaned_data['delete']:
                # get the relevant TaggedItem
                ti = get_object_or_404(
                    TaggedItem, object_id=thisgloss.id, tag__name=tag)
                ti.delete()
                response = HttpResponse(
                    'deleted', content_type='text/plain')
            else:
                # we need to wrap the tag name in quotes since it might contain
                # spaces
                Tag.objects.add_tag(thisgloss, '"%s"' % tag)
                # response is new HTML for the tag list and form
                response = render(request, 'dictionary/glosstags.html',
                                  {'gloss': thisgloss, 'tagform': TagUpdateForm()})
        else:
            print ("invalid form")
            print((form.as_table()))
    return response


@login_required
@permission_required('dictionary.import_csv')
def import_gloss_csv(request):
    """
    Check which objects exist and which not. Then show the user a list of glosses that will be added if user confirms.
    Store the glosses to be added into sessions.
    """
    glosses_new = []
    glosses_exists = []
    # Make sure that the session variables are flushed before using this view.
    if 'dataset_id' in request.session: del request.session['dataset_id']
    if 'glosses_new' in request.session: del request.session['glosses_new']

    if request.method == 'POST':
        form = CSVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            dataset = form.cleaned_data['dataset']

            if 'view_dataset' not in get_perms(request.user, dataset):
                # If user has no permissions to dataset, raise PermissionDenied to show 403 template.
                msg = _("You do not have permissions to import glosses to this lexicon.")
                messages.error(request, msg)
                raise PermissionDenied(msg)

            try:
                glossreader = csv.reader(form.cleaned_data['file'], delimiter=',', quotechar='"')
            except csv.Error as e:
                # Can't open file, remove session variables
                if 'dataset_id' in request.session: del request.session['dataset_id']
                if 'glosses_new' in request.session: del request.session['glosses_new']
                # Set a message to be shown so that the user knows what is going on.
                messages.add_message(request, messages.ERROR, _('Cannot open the file:' + str(e)))
                return render(request, "dictionary/import_gloss_csv.html", {'import_csv_form': CSVUploadForm()}, )
            else:
                for row in glossreader:
                    if glossreader.line_num == 1:
                        # Skip first line of CSV file.
                        continue
                    try:
                        # Find out if the gloss already exists, if it does add to list of glosses not to be added.
                        gloss = Gloss.objects.get(dataset=dataset, idgloss=row[0])
                        glosses_exists.append(gloss)
                    except Gloss.DoesNotExist:
                        # If gloss is not already in list, add glossdata to list of glosses to be added as a tuple.
                        if not any(row[0] in s for s in glosses_new):
                            glosses_new.append(tuple(row))
                    except IndexError:
                        # If row[0] does not exist, continue to next iteration of loop.
                        continue
                # Store dataset's id and the list of glosses to be added in session.
                request.session['dataset_id'] = dataset.id
                request.session['glosses_new'] = glosses_new

            return render(request, "dictionary/import_gloss_csv_confirmation.html",
                          {#'import_csv_form': CSVUploadForm(),
                           'glosses_new': glosses_new,
                           'glosses_exists': glosses_exists,
                            'dataset': dataset,})
        else:
            # If form is not valid, set a error message and return to the original form.
            messages.add_message(request, messages.ERROR, _('The provided CSV-file does not meet the requirements '
                                                            'or there is some other problem.'))
            return render(request, "dictionary/import_gloss_csv.html", {'import_csv_form': CSVUploadForm()}, )
    else:
        # If request type is not POST, return to the original form.
        csv_form = CSVUploadForm()
        allowed_datasets = get_objects_for_user(request.user, 'dictionary.view_dataset')
        # Make sure we only list datasets the user has permissions to.
        csv_form.fields["dataset"].queryset = csv_form.fields["dataset"].queryset.filter(
            id__in=[x.id for x in allowed_datasets])
        return render(request, "dictionary/import_gloss_csv.html",
                      {'import_csv_form': csv_form}, )


@login_required
@permission_required('dictionary.import_csv')
def confirm_import_gloss_csv(request):
    """This view adds the data to database if the user confirms the action"""
    if request.method == 'POST':
        if 'cancel' in request.POST:
            # If user cancels adding data, flush session variables
            if 'dataset_id' in request.session: del request.session['dataset_id']
            if 'glosses_new' in request.session: del request.session['glosses_new']
            # Set a message to be shown so that the user knows what is going on.
            messages.add_message(request, messages.WARNING, _('Cancelled adding CSV data.'))
            return HttpResponseRedirect(reverse('dictionary:import_gloss_csv'))

        elif 'confirm' in request.POST:
            glosses_added = []
            dataset = None
            if 'glosses_new' and 'dataset_id' in request.session:
                dataset = Dataset.objects.get(id=request.session['dataset_id'])
                for gloss in request.session['glosses_new']:

                    # If the Gloss does not already exist, continue adding.
                    if not Gloss.objects.filter(dataset=dataset, idgloss=gloss[0]).exists():
                        try:
                            new_gloss = Gloss(dataset=dataset, idgloss=gloss[0], idgloss_en=gloss[1],
                                          created_by=request.user, updated_by=request.user)
                        except IndexError:
                            # If we get IndexError, idgloss_en was probably not provided
                            new_gloss = Gloss(dataset=dataset, idgloss=gloss[0],
                                              created_by=request.user, updated_by=request.user)

                        new_gloss.save()
                        glosses_added.append((new_gloss.idgloss, new_gloss.idgloss_en))

                # Flush request.session['glosses_new'] and request.session['dataset']
                del request.session['glosses_new']
                del request.session['dataset_id']
                # Set a message to be shown so that the user knows what is going on.
                messages.add_message(request, messages.SUCCESS, _('Glosses were added succesfully.'))
            return render(request, "dictionary/import_gloss_csv_confirmation.html", {'glosses_added': glosses_added,
                                                                                     'dataset': dataset.name})
        else:
            return HttpResponseRedirect(reverse('dictionary:import_gloss_csv'))
    else:
        # If request method is not POST, redirect to the import form
        return HttpResponseRedirect(reverse('dictionary:import_gloss_csv'))


def gloss_relation(request):
    """Processes Gloss Relations"""
    if request.method == "POST":
        form = GlossRelationForm(request.POST)
        if "delete" in form.data:
            glossrelation = get_object_or_404(GlossRelation, id=int(form.data["delete"]))
            if 'view_dataset' not in get_perms(request.user, glossrelation.source.dataset):
                # If user has no permissions to dataset, raise PermissionDenied to show 403 template.
                msg = _("You do not have permissions to delete relations from glosses of this lexicon.")
                messages.error(request, msg)
                raise PermissionDenied(msg)
            ct = ContentType.objects.get_for_model(GlossRelation)
            # Delete TaggedItems and the GlossRelation
            TaggedItem.objects.filter(object_id=glossrelation.id, content_type=ct).delete()
            glossrelation.delete()

            if "HTTP_REFERER" in request.META:
                return redirect(request.META["HTTP_REFERER"])
            return redirect("/")

        if form.is_valid():
            source = get_object_or_404(Gloss, id=form.cleaned_data["source"])
            if 'view_dataset' not in get_perms(request.user, source.dataset):
                # If user has no permissions to dataset, raise PermissionDenied to show 403 template.
                msg = _("You do not have permissions to add relations to glosses of this lexicon.")
                messages.error(request, msg)
                raise PermissionDenied(msg)
            target = get_object_or_404(Gloss, id=form.cleaned_data["target"])
            glossrelation = GlossRelation.objects.create(source=source, target=target)
            if form.cleaned_data["tag"]:
                Tag.objects.add_tag(glossrelation, form.cleaned_data["tag"].name)
            if "HTTP_REFERER" in request.META:
                return redirect(request.META["HTTP_REFERER"])
            return redirect("/")
        from django.http import HttpResponseBadRequest
        return HttpResponseBadRequest("Bad request.")
