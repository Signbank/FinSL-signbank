from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden, HttpResponseBadRequest
from django.template import Context, RequestContext, loader
from django.http import Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.core.urlresolvers import reverse
from django.conf import settings
from django.contrib.auth.decorators import permission_required
from django.db.models.fields import NullBooleanField

from signbank.log import debug
from tagging.models import TaggedItem, Tag
import os
import shutil
import re

from signbank.video.models import GlossVideo
from signbank.dictionary.models import *
from signbank.dictionary.forms import *
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ObjectDoesNotExist


@permission_required('dictionary.add_gloss')
def add_gloss(request):
    if request.method == 'POST':
        form = GlossCreateForm(request.POST)
        if form.is_valid():
            new_gloss = form.save()
            return HttpResponseRedirect(reverse('dictionary:admin_gloss_list'))
    else:
        form = GlossCreateForm()
    return render_to_response('dictionary/add_gloss.html',
                              {'add_gloss_form': form},
                              context_instance=RequestContext(request))

def update_gloss(request, glossid):
    """View to update a gloss model from the jeditable jquery form
    We are sent one field and value at a time, return the new value
    once we've updated it."""

    if not request.user.has_perm('dictionary.change_gloss'):
        # Translators: HttpResponseForbidden for update_gloss
        return HttpResponseForbidden(_("Gloss Update Not Allowed"))

    if request.method == "POST":

        gloss = get_object_or_404(Gloss, id=glossid)
        old_idgloss = unicode(gloss)


        field = request.POST.get('id', '')
        value = request.POST.get('value', '')

        if len(value) == 0:
            value = ' '

        elif value[0] == '_':
            value = value[1:]

        # in case we need multiple values
        values = request.POST.getlist('value[]')

        # validate
        # field is a valid field
        # value is a valid value for field
        # NOTICE: if you edit some field names, it can break things. Some fiels are checked with startswith!
        if field == 'deletegloss':
            if value == 'confirmed':
                # delete the gloss and redirect back to gloss list
                gloss.delete()
                return HttpResponseRedirect(reverse('dictionary:admin_gloss_list'))

        if field.startswith('definition'):

            return update_definition(request, gloss, field, value)

        elif field == 'keywords':

            return update_keywords(gloss, field, value)

        elif field == 'keywords_english':

            return update_keywords_english(gloss, field, value)

        elif field.startswith('relationforeign'):

            return update_relationtoforeignsign(gloss, field, value)

        # Had to add field != 'relation_between_articulators' because I changed its field name, and it conflicted here.
        elif field.startswith('relation') and field != 'relation_between_articulators':

            return update_relation(gloss, field, value)

        elif field.startswith('morphology-definition'):

            return update_morphology_definition(gloss, field, value)

        elif field == 'language':
            # expecting possibly multiple values

            try:
                gloss.language.clear()
                for value in values:
                    lang = Language.objects.get(name=value)
                    gloss.language.add(lang)
                gloss.save()
                newvalue = ", ".join([unicode(g) for g in gloss.language.all()])
            except:
                # Translators: HttpResponseBadRequest
                return HttpResponseBadRequest("%s %s" % _("Uknown Language"), values, content_type='text/plain')

        elif field == 'dialect':
            # expecting possibly multiple values

            try:
                gloss.dialect.clear()
                for value in values:
                    lang = Dialect.objects.get(name=value)
                    gloss.dialect.add(lang)
                gloss.save()
                newvalue = ", ".join([unicode(g.name)
                                      for g in gloss.dialect.all()])
            except:
                # Translators: HttpResponseBadRequest
                return HttpResponseBadRequest("%s %s" % _("Unknown Dialect"), values, content_type='text/plain')

        elif field == "sn":
            # sign number must be unique, return error message if this SN is
            # already taken

            if value == '':
                gloss.__setattr__(field, None)
                gloss.save()
                newvalue = ''
            else:
                try:
                    value = int(value)
                except:
                    # Translators: HttpResponseBadRequest
                    return HttpResponseBadRequest(_("SN value must be integer"), content_type='text/plain')

                existing_gloss = Gloss.objects.filter(sn__exact=value)
                if existing_gloss.count() > 0:
                    g = existing_gloss[0].idgloss
                    # Translators: HttpResponseBadRequest
                    return HttpResponseBadRequest("%s %s" % _("SN value already taken for gloss"), g,
                                                  content_type='text/plain')
                else:
                    gloss.sn = value
                    gloss.save()
                    newvalue = value

        elif field == 'in_web_dictionary':
            # only modify if we have publish permission
            if request.user.has_perm('dictionary.can_publish'):
                gloss.in_web_dictionary = (value == 'Yes')
                gloss.save()

            if gloss.in_web_dictionary:
                newvalue = 'Yes'
            else:
                newvalue = 'No'

        else:

            if not field in Gloss._meta.get_all_field_names():
                # Translators: HttpResponseBadRequest
                return HttpResponseBadRequest(_("Unknown field"), content_type='text/plain')

            # special cases
            # - Foreign Key fields (Language, Dialect)
            # - keywords
            # - videos
            # - tags

            # Translate the value if a boolean
            if isinstance(gloss._meta.get_field_by_name(field)[0], NullBooleanField):
                newvalue = value
                value = (value == 'Yes')

            # special value of 'notset' or -1 means remove the value
            if value == 'notset' or value == -1 or value == '':
                gloss.__setattr__(field, None)
                gloss.save()
                newvalue = ''
            else:

                # TODO: Check these changes later on
                # gloss.__setattr__(field, value)
                # See if the field is a ForeignKey
                if gloss._meta.get_field_by_name(field)[0].get_internal_type() == "ForeignKey":
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
                        valdict = dict(get_choices_with_int(field))
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
            # TODO: Implement this as a method, and place it someplace useful
            if field == 'idgloss' and newvalue != old_idgloss:
                try:
                    glossvideo = GlossVideo.objects.get(gloss=gloss)
                    new_path = 'glossvideo/' + unicode(gloss.idgloss[:2]) + '/' + \
                           unicode(gloss) + '-' + unicode(gloss.pk) + '.mp4'
                    new_path_full = settings.MEDIA_ROOT + '/' + new_path
                    os.rename(glossvideo.videofile.path, new_path_full)
                    glossvideo.videofile.name = new_path
                    glossvideo.save()
                except:
                    #gloss.idgloss = old_idgloss
                    pass

        return HttpResponse(newvalue, content_type='text/plain')


# Updates keywords for the 1st language
def update_keywords(gloss, field, value):
    """Update the keyword field"""

    kwds = [k.strip() for k in value.split(',')]
    # remove current keywords
    current_trans = gloss.translation_set.all()
    # current_kwds = [t.translation for t in current_trans]
    current_trans.delete()
    # add new keywords
    for i in range(len(kwds)):
        (kobj, created) = Keyword.objects.get_or_create(text=kwds[i])
        trans = Translation(gloss=gloss, translation=kobj, index=i)
        trans.save()

    newvalue = ", ".join(
        [t.translation.text for t in gloss.translation_set.all()])

    return HttpResponse(newvalue, content_type='text/plain')


# Updates English keywords
# The reason this method is copied is to keep it simpler.
def update_keywords_english(gloss, field, value):
    """Update the keyword field"""

    kwds = [k.strip() for k in value.split(',')]
    # remove current keywords
    current_trans = gloss.translationenglish_set.all()
    # current_kwds = [t.translation for t in current_trans]
    current_trans.delete()
    # add new keywords
    for i in range(len(kwds)):
        (kobj, created) = KeywordEnglish.objects.get_or_create(text=kwds[i])
        trans = TranslationEnglish(gloss=gloss, translation_english=kobj, index=i)
        trans.save()

    newvalue = ", ".join(
        [t.translation_english.text for t in gloss.translationenglish_set.all()])

    return HttpResponse(newvalue, content_type='text/plain')


def update_relation(gloss, field, value):
    """Update one of the relations for this gloss"""

    (what, relid) = field.split('_')
    what = what.replace('-', '_')

    try:
        rel = Relation.objects.get(id=relid)
    except:
        # Translators: HttpResponseBadRequest
        return HttpResponseBadRequest("%s '%s'" % _("Bad Relation ID"), relid, content_type='text/plain')

    if not rel.source == gloss:
        # Translators: HttpResponseBadRequest
        return HttpResponseBadRequest(_("Relation doesn't match gloss"), content_type='text/plain')

    if what == 'relationdelete':
        print "DELETE: ", rel
        rel.delete()
        return HttpResponseRedirect(reverse('dictionary:admin_gloss_view', kwargs={'pk': gloss.id}))
    elif what == 'relationrole':
        #rel.role = value
        try:
            rel.role = FieldChoice.objects.get(machine_value=value)
        except:
            rel.role = value
        rel.save()
        #newvalue = rel.get_role_display()
        newvalue = rel.role
    elif what == 'relationtarget':

        target = gloss_from_identifier(value)
        if target:
            rel.target = target
            rel.save()
            newvalue = unicode(target)
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
    except:
        # Translators: HttpResponseBadRequest
        return HttpResponseBadRequest("%s '%s'" % _("Bad RelationToForeignSign ID"), relid,
                                      content_type='text/plain')

    if not rel.gloss == gloss:
        # Translators: HttpResponseBadRequest
        return HttpResponseBadRequest(_("Relation doesn't match gloss"), content_type='text/plain')

    if what == 'relationforeigndelete':
        print "DELETE: ", rel
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
    except:
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
            except:
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
            print form

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
            except:
                # Translators: HttpResponseBadRequest
                return HttpResponseBadRequest(_("Source gloss not found."), content_type='text/plain')

            rel = RelationToForeignSign(gloss=gloss, loan=loan, other_lang=other_lang,
                                        other_lang_gloss=other_lang_gloss)
            rel.save()

            return HttpResponseRedirect(
                reverse('dictionary:admin_gloss_view', kwargs={'pk': gloss.id}) + '?editrelforeign')

        else:
            print form
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
    except:
        # Translators: HttpResponseBadRequest
        return HttpResponseBadRequest("%s '%s'" % _("Bad Morphology Definition ID"), morph_def_id,
                                      content_type='text/plain')

    if not morph_def.parent_gloss == gloss:
        # Translators: HttpResponseBadRequest
        return HttpResponseBadRequest(_("Morphology Definition doesn't match gloss"), content_type='text/plain')

    if what == 'morphology_definition_delete':
        print "DELETE: ", morph_def
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
            newvalue = unicode(morpheme)
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
                response = render_to_response('dictionary/glosstags.html',
                                              {'gloss': thisgloss,
                                               'tagform': TagUpdateForm(),
                                               },
                                              context_instance=RequestContext(request))
        else:
            print "invalid form"
            print form.as_table()

    return response
