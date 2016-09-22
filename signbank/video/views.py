from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import permission_required
from models import GlossVideo
from forms import VideoUploadForGlossForm
from signbank.dictionary.models import Gloss


@permission_required('dictionary.add_gloss')
def addvideo(request):
    """View to present a video upload form and process the upload"""

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
            video.videofile = vfile
            video.save()

            # TODO: provide some feedback that it worked (if immediate display of video isn't working)

            redirect_url = form.cleaned_data['redirect']

            return redirect(redirect_url)

    # if we can't process the form, just redirect back to the
    # referring page, should just be the case of hitting
    # Upload without choosing a file but could be
    # a malicious request, if no referrer, go back to root
    if 'HTTP_REFERER' in request.META:
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
