from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext
from django.conf import settings
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _

from signbank.feedback.forms import *


def index(request):
    return render_to_response('feedback/index.html',
                              {
                                  'language': settings.LANGUAGE_NAME,
                                  'country': settings.COUNTRY_NAME,
                                  # Translators: Title for feedback views index
                                  'title': _("Leave Feedback")},
                              context_instance=RequestContext(request))

@login_required(login_url='/accounts/login/')
def generalfeedback(request):
    feedback = GeneralFeedback()
    valid = False

    if request.method == "POST":
        form = GeneralFeedbackForm(request.POST, request.FILES)
        if form.is_valid():

            feedback = GeneralFeedback(user=request.user)
            if form.cleaned_data.has_key('comment'):
                feedback.comment = form.cleaned_data['comment']

            if form.cleaned_data.has_key('video') and form.cleaned_data['video'] is not None:
                feedback.video = form.cleaned_data['video']

            feedback.save()
            valid = True
    else:
        form = GeneralFeedbackForm()

    return render_to_response("feedback/generalfeedback.html",
                              {
                                  'language': settings.LANGUAGE_NAME,
                                  'country': settings.COUNTRY_NAME,
                                  # Translators: General Feedback title
                                  'title': _("General Feedback"),
                                  'form': form,
                                  'valid': valid},
                              context_instance=RequestContext(request)
                              )


@login_required(login_url='/accounts/login/')
def missingsign(request):
    posted = False  # was the feedback posted?

    if request.method == "POST":

        fb = MissingSignFeedback()
        fb.user = request.user

        form = MissingSignFeedbackForm(request.POST, request.FILES)

        if form.is_valid():

            # either we get video of the new sign or we get the
            # description via the form

            if form.cleaned_data.has_key('video') and form.cleaned_data['video'] is not None:
                fb.video = form.cleaned_data['video']

            else:
                # get sign details from the form
                fb.handform = form.cleaned_data['handform']
                fb.handshape = form.cleaned_data['handshape']
                fb.althandshape = form.cleaned_data['althandshape']
                fb.location = form.cleaned_data['location']
                fb.relativelocation = form.cleaned_data['relativelocation']
                fb.handbodycontact = form.cleaned_data['handbodycontact']
                fb.handinteraction = form.cleaned_data['handinteraction']
                fb.direction = form.cleaned_data['direction']
                fb.movementtype = form.cleaned_data['movementtype']
                fb.smallmovement = form.cleaned_data['smallmovement']
                fb.repetition = form.cleaned_data['repetition']

            # these last two are required either way (video or not)
            fb.meaning = form.cleaned_data['meaning']
            fb.comments = form.cleaned_data['comments']

            fb.save()
            posted = True
    else:
        form = MissingSignFeedbackForm()

    return render_to_response('feedback/missingsign.html',
                              {
                                  'language': settings.LANGUAGE_NAME,
                                  'country': settings.COUNTRY_NAME,
                                  # Translators Report Missing Sign title
                                  'title': _("Report a Missing Sign"),
                                  'posted': posted,
                                  'form': form
                              },
                              context_instance=RequestContext(request))


# -----------
# views to show feedback to Trevor et al
# -----------

@permission_required('feedback.delete_generalfeedback')
def showfeedback(request):
    """View to list the feedback that's been left on the site"""

    general = GeneralFeedback.objects.filter(status='unread')
    missing = MissingSignFeedback.objects.filter(status='unread')
    signfb = SignFeedback.objects.filter(status__in=('unread', 'read'))

    return render_to_response("feedback/show.html",
                              {'general': general,
                               'missing': missing,
                               'signfb': signfb,
                               },
                              context_instance=RequestContext(request))


@login_required(login_url='/accounts/login/')
def glossfeedback(request, glossid):
    gloss = get_object_or_404(Gloss, idgloss=glossid)

    # construct a translation so we can record feedback against it
    # really should have recorded feedback for a gloss, not a sign
    allkwds = gloss.translation_set.all()
    allkwds_en = gloss.translationenglish_set.all()

    if len(allkwds) == 0:
        trans = Translation()
    else:
        trans = allkwds[0]
    if len(allkwds_en) == 0:
        trans_en = TranslationEnglish()
    else:
        trans_en = allkwds_en[0]

    return recordsignfeedback(request, trans, 1, len(allkwds), trans_en, 1, len(allkwds_en))


# Feedback on individual signs
@login_required(login_url='/accounts/login/')
def signfeedback(request, keyword, n):
    """View or give feedback on a sign"""

    n = int(n)
    word = get_object_or_404(Keyword, text=keyword)

    # returns (matching translation, number of matches)
    (trans, total) = word.match_request(request, n)

    return recordsignfeedback(request, trans, n, total)


def recordsignfeedback(request, trans, n, total, trans_en, n_en, total_en):
    """Do the work of recording feedback for a sign or gloss"""

    # get the page to return to from the get request
    if request.GET.has_key('return'):
        sourcepage = request.GET['return']
    else:
        sourcepage = ""

    if request.GET.has_key('lastmatch'):
        lastmatch = request.GET['lastmatch']
    else:
        lastmatch = None

    valid = False

    if request.method == "POST":
        feedback_form = SignFeedbackForm(request.POST)

        if feedback_form.is_valid():
            # get the clean (normalised) data from the feedback_form
            clean = feedback_form.cleaned_data
            # create a SignFeedback object to store the result in the db

            sfb = SignFeedback(
                isAuslan=clean['isAuslan'],
                whereused=clean['whereused'],
                like=clean['like'],
                use=clean['use'],
                suggested=clean['suggested'],
                correct=clean['correct'],
                kwnotbelong=clean['kwnotbelong'],
                comment=clean['comment'],
                user=request.user,
                # translation_id=request.POST['translation_id']
            )
            # Here we are hacking away this problem when there is no translation
            # for a Gloss. Because translation_id is int, it doesn't accept None.
            this_translation_id = request.POST['translation_id']
            if this_translation_id != 'None':
                sfb.translation_id = this_translation_id
            sfb.save()
            valid = True
            # redirect to the original page
            if lastmatch:
                return HttpResponseRedirect(
                    # sourcepage + "?lastmatch=" + lastmatch + "&feedbackmessage=" + _(
                    #    "Thank you. Your feedback has been saved."))
                    "%s%s%s%s%s" % (sourcepage, "?lastmatch=", lastmatch, "&feedbackmessage=",
                                    # Translators: Thank you message for recording signfeedback
                                    _("Thank you. Your feedback has been saved.")))
            else:
                return HttpResponseRedirect(
                    # sourcepage + "?feedbackmessage=" + _("Thank you. Your feedback has been saved."))
                    "%s%s%s" % (sourcepage, "?feedbackmessage=",
                                # Translators: Thank you message for recording signfeedback
                                _("Thank you. Your feedback has been saved.")))
    else:
        feedback_form = SignFeedbackForm()

    return render_to_response("feedback/signfeedback.html",
                              {'translation': trans,
                               'n': n,
                               'total': total,
                               'translation_english': trans_en,
                               'n_en': n_en,
                               'total_en': total_en,
                               'feedback_form': feedback_form,
                               'valid': valid,
                               'sourcepage': sourcepage,
                               'lastmatch': lastmatch,
                               'language': settings.LANGUAGE_NAME,
                               },
                              context_instance=RequestContext(request))


# --------------------
#  deleting feedback
# --------------------
@permission_required('feedback.delete_generalfeedback')
def delete(request, kind, id):
    """Mark a feedback item as deleted, kind 'signfeedback', 'generalfeedback' or 'missingsign'"""

    if kind == 'sign':
        kind = SignFeedback
    elif kind == 'general':
        kind = GeneralFeedback
    elif kind == 'missingsign':
        kind = MissingSignFeedback
    else:
        raise Http404

    item = get_object_or_404(kind, id=id)
    # mark as deleted
    item.status = 'deleted'
    item.save()

    # return to referer
    if request.META.has_key('HTTP_REFERER'):
        url = request.META['HTTP_REFERER']
    else:
        url = '/'
    return redirect(url)
