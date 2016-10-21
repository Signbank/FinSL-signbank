from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import permission_required
from django.views.generic.edit import FormView
from django.views.generic.list import ListView
from models import GlossVideo
from forms import VideoUploadForGlossForm, MultipleVideoUploadForm
from signbank.dictionary.models import Gloss
from .forms import UpdateGlossVideoForm


@permission_required('video.add_glossvideo')
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


class AddVideosView(FormView):
    """View for multiple video file upload. These videos will have no connection to glosses."""
    form_class = MultipleVideoUploadForm
    template_name = 'addvideos.html'
    success_url = '/video/add/'

    def post(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        files = request.FILES.getlist('file_field')
        if form.is_valid():
            data = form.cleaned_data
            dataset = data['dataset']
            for f in files:
                GlossVideo.objects.create(videofile=f, dataset=dataset)
            return self.form_valid(form)
        else:
            return self.form_invalid(form)


class GlossVideosNoGlossListView(ListView):
    model = GlossVideo
    template_name = 'videos_with_no_gloss.html'
    paginate_by = 10
    context_object_name = 'videos'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(GlossVideosNoGlossListView, self).get_context_data(**kwargs)
        page = self.request.GET.get('page')
        context['page'] = page
        # Set get params in form
        form = UpdateGlossVideoForm(self.request.GET)
        if 'dataset' in self.request.GET and self.request.GET.get('dataset'):
            # Set queryset for form.gloss
            form.fields["gloss"].queryset = Gloss.objects.filter(dataset__pk=self.request.GET.get("dataset"))
        context['form'] = form
        return context

    def get_queryset(self):
        qs = GlossVideo.objects.filter(gloss=None)
        get = self.request.GET
        if 'dataset' in get and self.request.GET.get('dataset'):
            # Filter based on param dataset
            qs = qs.filter(dataset=get['dataset'])
        if 'page' in get:
            page = self.request.GET.get('page')
        else:
            page = 0
        return qs

    def render_to_response(self, context, **response_kwargs):
        return super(GlossVideosNoGlossListView, self).render_to_response(context)


@permission_required('video.change_glossvideo')
def update_glossvideo(request):
    """Here we process the post request for updating a glossvideo."""
    if request.method == 'POST':
        post = request.POST
        if 'gloss' in post and 'glossvideo' in post:
            glossvideo = GlossVideo.objects.get(pk=post['glossvideo'])
            glossvideo.gloss = Gloss.objects.get(pk=post['gloss'])
            glossvideo.save()
    if "HTTP_REFERER" in request.META:
        return redirect(request.META["HTTP_REFERER"])
    return redirect("/")


def poster(request, videoid):
    """Generate a still frame for a video (if needed) and
    generate a redirect to the static server for this frame"""

    video = get_object_or_404(GlossVideo, pk=videoid)

    return redirect(video.poster_url())


def video(request, videoid):
    """Redirect to the video url for this videoid"""

    video = get_object_or_404(GlossVideo, pk=videoid)

    return redirect(video)
