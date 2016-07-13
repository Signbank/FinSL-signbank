from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.conf import settings

from models import GlossVideo
from forms import VideoUploadForGlossForm
from signbank.dictionary.models import Gloss


def addvideo(request):
    """View to present a video upload form and process
    the upload"""

    if request.method == 'POST':

        form = VideoUploadForGlossForm(request.POST, request.FILES)
        if form.is_valid():

            gloss_id = form.cleaned_data['gloss_id']
            gloss = get_object_or_404(Gloss, pk=gloss_id)

            vfile = form.cleaned_data['videofile']

            video = GlossVideo(gloss=gloss)
            # Save the GlossVideo to get a primary key
            video.save()

            # Construct a filename for the video
            vfile.name = GlossVideo.create_filename(gloss.idgloss, gloss.pk, video.pk)

            # deal with any existing video for this sign
            #oldvids = GlossVideo.objects.filter(gloss=gloss)
            #for v in oldvids:
            #    v.reversion()

            video.videofile=vfile
            video.save()

            # TODO: provide some feedback that it worked (if
            # immediate display of video isn't working)

            redirect_url = form.cleaned_data['redirect']

            return redirect(redirect_url)

    # if we can't process the form, just redirect back to the
    # referring page, should just be the case of hitting
    # Upload without choosing a file but could be
    # a malicious request, if no referrer, go back to root
    if request.META.has_key('HTTP_REFERER'):
        url = request.META['HTTP_REFERER']
    else:
        url = '/'
    return redirect(url)


@login_required(login_url='/accounts/login/')
def deletevideo(request, videoid):
    """Remove the video for this gloss, if there is an older version
    then reinstate that as the current video (act like undo)"""

    if request.method == "POST":
        # deal with any existing video for this sign
        gloss = get_object_or_404(Gloss, pk=videoid)
        vids = GlossVideo.objects.filter(gloss=gloss).order_by('version')
        for v in vids:
            # this will remove the most recent video, ie it's equivalent
            # to delete if version=0
            v.reversion(revert=True)

    # TODO: provide some feedback that it worked (if
    # immediate non-display of video isn't working)

    # return to referer
    if request.META.has_key('HTTP_REFERER'):
        url = request.META['HTTP_REFERER']
    else:
        url = '/'
    return redirect(url)


def poster(request, videoid):
    """Generate a still frame for a video (if needed) and
    generate a redirect to the static server for this frame"""

    video = get_object_or_404(GlossVideo, gloss_id=videoid)

    return redirect(video.poster_url())


def video(request, videoid):
    """Redirect to the video url for this videoid"""

    video = get_object_or_404(GlossVideo, gloss_id=videoid)

    return redirect(video)


def iframe(request, videoid):
    """Generate an iframe with a player for this video"""

    try:
        gloss = Gloss.objects.get(pk=videoid)
        glossvideo = gloss.get_video() # TODO: Why is this getting the video from 'dictionary.gloss'?

        videourl = glossvideo.get_absolute_url()

        posterurl = glossvideo.poster_url()
    except Gloss.DoesNotExist:
        videourl = None
        posterurl = None

    return render_to_response("iframe.html",
                              {'videourl': videourl,
                               'posterurl': posterurl,
                               'aspectRatio': settings.VIDEO_ASPECT_RATIO,
                               },
                              context_instance=RequestContext(request))
