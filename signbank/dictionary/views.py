import csv

from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.decorators import login_required
from tagging.models import TaggedItem
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.exceptions import ObjectDoesNotExist
from django.utils.encoding import smart_unicode

from signbank.dictionary.forms import *
from signbank.feedback.models import *
from signbank.dictionary.update import update_keywords
import forms
from signbank.video.forms import VideoUploadForGlossForm
from signbank.tools import video_to_signbank, compare_valuedict_to_gloss
from django.contrib.admin.views.decorators import user_passes_test

from django.utils.translation import ugettext_lazy as _

@login_required(login_url='/accounts/login/')
def index(request):
    """Default view showing a browse/search entry
    point to the dictionary"""

    return render_to_response("dictionary/search_result.html",
                              {'form': UserSignSearchForm(),
                               'language': settings.LANGUAGE_NAME,
                               'query': '',
                               },
                              context_instance=RequestContext(request))

@login_required(login_url='/accounts/login/')
# Default values for keyword_english and n_en are None
# n is the amount of hits we get for one keyword
def word(request, keyword, n, keyword_english=None, n_en=None):
    """View of a single keyword that may have more than one sign"""

    n = int(n)
    # Added this in try-block because I am not sure where this method is used from. Just added the keyword_english
    # stuff here, which may not always be sent.
    try:
        n_en = int(n_en)
    except ValueError:
        pass

    if request.GET.has_key('feedbackmessage'):
        feedbackmessage = request.GET['feedbackmessage']
    else:
        feedbackmessage = False

    word = get_object_or_404(Keyword, text=keyword)
    # TODO: Enable?
    # word_en = get_object_or_404(KeywordEnglish, text=keyword_english)

    # TODO: Implement / check these KeywordEnglish features
    # returns (matching translation, number of matches)
    (trans, total) = word.match_request(request, n, )

    # returns (matching English translation, number of matches)
    # TODO: enable?
    # (trans_en, total_en) = word.match_request_english(request, n_en, )

    # and all the keywords associated with this sign
    allkwds = trans.gloss.translation_set.all()

    # and all the keywords associated with this sign
    # TODO: enable?
    # allkwds_en = trans_en.gloss.translationenglish_set.all()

    videourl = trans.gloss.get_video_url()
    if not os.path.exists(os.path.join(settings.MEDIA_ROOT, videourl)):
        videourl = None

    # work out the number of this gloss and the total number TODO: is this needed
    gloss = trans.gloss

    # the gloss update form for staff
    if request.user.has_perm('dictionary.search_gloss'):
        update_form = GlossModelForm(instance=trans.gloss)
        video_form = VideoUploadForGlossForm(initial={'gloss_id': trans.gloss.pk,
                                                      'redirect': request.path})
    else:
        update_form = None
        video_form = None

    return render_to_response("dictionary/word.html",
                              {'translation': trans.translation.text.encode('utf-8'),
                               # Added this to support English translations
                               # TODO: disabled temporarily
                               # 'translationenglish:': trans_en.translation_english.text.encode('utf-8'),
                               'viewname': 'words',
                               'definitions': trans.gloss.definitions(),
                               'gloss': trans.gloss,
                               'allkwds': allkwds,
                               # TODO: disabled temporarily
                               # 'allkwds_en': allkwds_en,
                               'n': n,
                               'total': total,
                               'matches': range(1, total + 1),
                               # lastmatch is a construction of the url for this word
                               # view that we use to pass to gloss pages
                               # could do with being a fn call to generate this
                               # name here and elsewhere
                               'lastmatch': trans.translation.text.encode('utf-8') + "-" + str(n),
                               'videofile': videourl,
                               'update_form': update_form,
                               'videoform': video_form,
                               #'gloss': gloss,
                               'glosscount': 0,
                               'feedback': True,
                               'feedbackmessage': feedbackmessage,
                               'tagform': TagUpdateForm(),
                               'DEFINITION_FIELDS': settings.DEFINITION_FIELDS,
                               },
                              context_instance=RequestContext(request))


@login_required(login_url='/accounts/login/')
def gloss(request, idgloss):
    """View of a gloss - mimics the word view, really for admin use
       when we want to preview a particular gloss"""

    if request.GET.has_key('feedbackmessage'):
        feedbackmessage = request.GET['feedbackmessage']
    else:
        feedbackmessage = False

    # we should only be able to get a single gloss, but since the URL
    # pattern could be spoofed, we might get zero or many
    # so we filter first and raise a 404 if we don't get one
    glosses = Gloss.objects.filter(idgloss=idgloss)

    if len(glosses) != 1:
        raise Http404

    gloss = glosses[0]

    # and all the keywords associated with this sign
    allkwds = gloss.translation_set.all()
    if len(allkwds) == 0:
        trans = Translation()
    else:
        trans = allkwds[0]

    # and all the English keywords associated with this sign
    allkwds_en = gloss.translationenglish_set.all()
    if len(allkwds_en) == 0:
        trans_en = TranslationEnglish()
    else:
        trans_en = allkwds[0]

    videourl = gloss.get_video_url()
    if not os.path.exists(os.path.join(settings.MEDIA_ROOT, videourl)):
        videourl = None

    # the gloss update form for staff
    update_form = None

    if request.user.has_perm('dictionary.search_gloss'):
        update_form = GlossModelForm(instance=gloss)
        video_form = VideoUploadForGlossForm(initial={'gloss_id': gloss.pk,
                                                      'redirect': request.get_full_path()})
    else:
        update_form = None
        video_form = None

    # get the last match keyword if there is one passed along as a form
    # variable
    if request.GET.has_key('lastmatch'):
        lastmatch = request.GET['lastmatch']
        if lastmatch == "None":
            lastmatch = False
    else:
        lastmatch = False

    return render_to_response("dictionary/word.html",
                              {'translation': trans,
                               'translationenglish': trans_en,
                               'definitions': gloss.definitions(),
                               'allkwds': allkwds,
                               'allkwds_en': allkwds_en,
                               'lastmatch': lastmatch,
                               'videofile': videourl,
                               'viewname': word,
                               'feedback': None,
                               'gloss': gloss,
                               'glosscount': 0, #TODO: needed?
                               'update_form': update_form,
                               'videoform': video_form,
                               'tagform': TagUpdateForm(),
                               'feedbackmessage': feedbackmessage,
                               'DEFINITION_FIELDS': settings.DEFINITION_FIELDS,
                               },
                              context_instance=RequestContext(request))


@login_required(login_url='/accounts/login/')
def search(request):
    """Handle keyword search form submission"""
    """
    if not (request.user.is_staff) and len(request.user.groups.filter(name="Publisher")) == 0 and len(
            request.user.groups.filter(name="Editor")) == 0:
        # Translators: Message sent if user is not allowed to see requested page.
        return HttpResponse(_('You are not allowed to see this page.'))
    """
    if not request.user.has_perm('dictionary.search_gloss'):
        # Translators: If user doesn't have permission search_gloss, show this text.
        return HttpResponse(_('You are not allowed to see this page.'))


    form = UserSignSearchForm(request.GET.copy())

    if form.is_valid():
        """
        These two redirects 'if glossQuery & if query' basically make the rest of this search method
        useless. But keeping them for reference if the public search needs to be enabled at some point.
        """

        glossQuery = form.cleaned_data['glossQuery']
        # From the menu searchbar using the gloss search, it redirects here
        # If the glossQuery field has values, redirect the search to adminviews.py
        # and use GET searchfield search to search for glosses.
        if glossQuery != '':
            return HttpResponseRedirect('../../signs/search/?search=' + glossQuery)

        query = form.cleaned_data['query']
        # From the menu searchbar using translation search, it redirects here
        # If query field has values, redirect the searc to adminviews.py via GET attribute
        # and set the GET field to be keyword, insert the searched keyword after it
        if query != '':
            return HttpResponseRedirect('../../signs/search/?keyword=' + query)

        # need to transcode the query to our encoding
        term = form.cleaned_data['query']
        category = form.cleaned_data['category']

        # safe search for authenticated users if the setting says so
        safe = (not request.user.is_authenticated()
                ) and settings.ANON_SAFE_SEARCH

        try:
            term = smart_unicode(term)
        except UnicodeError:
            # if the encoding didn't work this is a strange unicode or other string
            # and it won't match anything in the dictionary
            words = []

        if request.user.has_perm('dictionary.search_gloss'):
            # staff get to see all the words that have at least one translation
            words = Keyword.objects.filter(
                text__icontains=term, translation__isnull=False).distinct()
        else:
            # regular users see either everything that's published
            words = Keyword.objects.filter(text__icontains=term,
                                           translation__gloss__in_web_dictionary__exact=True).distinct()

        try:
            crudetag = Tag.objects.get(name='lexis:crude')
        except Tag.DoesNotExist:
            crudetag = None

        if safe and crudetag is not None:

            crude = TaggedItem.objects.get_by_model(Gloss, crudetag)
            # remove crude words from result

            result = []
            for w in words:
                # remove word if all glosses for any translation are tagged
                # crude
                trans = w.translation_set.all()
                glosses = [t.gloss for t in trans]

                if not all([g in crude for g in glosses]):
                    result.append(w)

            words = result

        if not category in ['all', '']:

            tag = Tag.objects.get(name=category)

            result = []
            for w in words:
                trans = w.translation_set.all()
                glosses = [t.gloss for t in trans]
                for g in glosses:
                    if tag in g.tags:
                        result.append(w)
            words = result

    else:
        term = ''
        words = []

    # display the keyword page if there's only one hit and it is an exact match
    if len(words) == 1 and words[0].text == term:
        return HttpResponseRedirect('/dictionary/words/' + words[0].text + '-1.html')

    paginator = Paginator(words, 50)
    if request.GET.has_key('page'):

        page = request.GET['page']
        try:
            result_page = paginator.page(page)
        except PageNotAnInteger:
            result_page = paginator.page(1)
        except EmptyPage:
            result_page = paginator.page(paginator.num_pages)

    else:
        result_page = paginator.page(1)

    return render_to_response("dictionary/search_result.html",
                              {'query': term,
                               'form': form,
                               'paginator': paginator,
                               'wordcount': len(words),
                               'page': result_page,
                               'ANON_SAFE_SEARCH': settings.ANON_SAFE_SEARCH,
                               'ANON_TAG_SEARCH': settings.ANON_TAG_SEARCH,
                               'language': settings.LANGUAGE_NAME,
                               },
                              context_instance=RequestContext(request))


def keyword_value_list(request, prefix=None):
    """View to generate a list of possible values for
    a keyword given a prefix."""

    kwds = Keyword.objects.filter(text__startswith=prefix)
    kwds_list = [k.text for k in kwds]
    return HttpResponse("\n".join(kwds_list), content_type='text/plain')

# Used by missing_video_view
@user_passes_test(lambda u:u.is_staff, login_url='/accounts/login/')
def missing_video_list():
    """A list of signs that don't have an
    associated video file"""

    glosses = Gloss.objects.filter(in_web_dictionary__exact=True)
    for gloss in glosses:
        if not gloss.has_video():
            yield gloss

# Don't find any use for this method
# I guess it looks for missing videos
@user_passes_test(lambda u:u.is_staff, login_url='/accounts/login/')
def missing_video_view(request):
    """A view for the above list"""

    glosses = missing_video_list()

    return render_to_response("dictionary/missingvideo.html",
                              {'glosses': glosses})


# No idea what this method is for. Do not use it.
"""
@user_passes_test(lambda u:u.is_staff, login_url='/accounts/login/')
def import_videos(request):
    video_folder = '/var/www2/signbank/live/writable/import_videos/' # TODO: Change this folder

    out = '<p>Imported</p><ul>'
    overwritten_files = '<p>Overwritten</p><ul>'

    for filename in os.listdir(video_folder):

        parts = filename.split('.')
        idgloss = '.'.join(parts[:-1])
        extension = parts[-1]

        try:
            gloss = Gloss.objects.get(idgloss=idgloss)
        except ObjectDoesNotExist:
            return HttpResponse(
                # Translators: HttpResponse if import_videos fails (Might not be useful to translate)
                _('Failed at ') + filename +
                # Translators: HttpResponse if import_videos fails (Might not be useful to translate)
                _('. Could not find ') + idgloss + '.')

        overwritten, was_allowed = video_to_signbank(
            video_folder, gloss, extension)

        if not was_allowed:
            return HttpResponse(
                # Translators: HttpResponse if import_videos fails (Might not be useful to translate)
                _('Failed two overwrite ') + gloss.idgloss +
                # Translators: HttpResponse if import_videos fails (Might not be useful to translate)
                _('. Maybe this file is not owned by the webserver?'))

        out += '<li>' + filename + '</li>'

        if overwritten:
            overwritten_files += '<li>' + filename + '</li>'

    out += '</ul>'
    overwritten_files += '</ul>'

    return HttpResponse(out + overwritten_files)
"""


@user_passes_test(lambda u:u.is_staff, login_url='/accounts/login/')
def try_code(request):
    """A view for the developer to try out things"""

    choicedict = {}

    for key, choices in choicedict.items():

        for machine_value, english_name in choices:
            FieldChoice(
                english_name=english_name, field=key, machine_value=machine_value).save()

    return HttpResponse('OK')

def add_new_sign(request):
    return render_to_response('dictionary/add_gloss.html', {'add_gloss_form': GlossCreateForm()},
                              context_instance=RequestContext(request))

def import_csv(request):
    if not request.user.is_staff and len(request.user.groups.filter(name="Publisher")) == 0:
        # Translators: import_csv: not allowed to see requested page (Might not be useful to translate)
        return HttpResponse(_('You are not allowed to see this page.'))

    uploadform = forms.CSVUploadForm
    changes = []

    # Propose changes
    if len(request.FILES) > 0:

        changes = []
        csv_lines = request.FILES['file'].read().split('\n')

        for nl, line in enumerate(csv_lines):

            # The first line contains the keys
            if nl == 0:
                keys = line.strip().split(',')
                continue
            elif len(line) == 0:
                continue

            values = csv.reader([line]).next()
            value_dict = {}

            for nv, value in enumerate(values):

                try:
                    value_dict[keys[nv]] = value
                except IndexError:
                    pass

            try:
                pk = int(value_dict['Signbank ID'])
            except ValueError:
                continue

            gloss = Gloss.objects.get(pk=pk)

            changes += compare_valuedict_to_gloss(value_dict, gloss)

        stage = 1

    # Do changes
    elif len(request.POST) > 0:

        for key, new_value in request.POST.items():

            try:
                pk, fieldname = key.split('.')

            # In case there's no dot, this is not a value we set at the
            # previous page
            except ValueError:
                continue

            gloss = Gloss.objects.get(pk=pk)

            # Updating the keywords is a special procedure, because it has
            # relations to other parts of the database
            if fieldname == 'Keywords':
                update_keywords(gloss, None, new_value)
                gloss.save()
                continue

            # Replace the value for bools
            if gloss._meta.get_field_by_name(fieldname)[0].__class__.__name__ == 'NullBooleanField':

                if new_value in ['true', 'True']:
                    new_value = True
                else:
                    new_value = False

            # The normal change and save procedure
            setattr(gloss, fieldname, new_value)
            gloss.save()

        stage = 2

    # Show uploadform
    else:

        stage = 0

    return render_to_response('dictionary/import_csv.html', {'form': uploadform, 'stage': stage, 'changes': changes},
                              context_instance=RequestContext(request))
