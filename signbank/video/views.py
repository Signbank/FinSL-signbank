from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import permission_required
from base64 import b64decode
from django.core.files.base import ContentFile
from django.views.generic.edit import FormView
from django.views.generic.list import ListView
from models import GlossVideo
from forms import VideoUploadForGlossForm, VideoUploadAddGlossForm, MultipleVideoUploadForm
from signbank.dictionary.models import Gloss
from .forms import UpdateGlossVideoForm, PosterUpload
from django.http import HttpResponse
import json
from os.path import splitext
from guardian.shortcuts import get_objects_for_user


def addvideo(request, gloss_id, redirect_url):
    """Add a video from form and process the upload"""
    if request.method == 'POST':
        form = VideoUploadAddGlossForm(request.POST, request.FILES)
        if form.is_valid():
            gloss = get_object_or_404(Gloss, pk=gloss_id)
            vfile = form.cleaned_data['videofile']
            video = GlossVideo(gloss=gloss)
            video_title = form.cleaned_data['video_title']
            if vfile: # If there is no video file, we don't want to create a glossvideo.
                if video_title: # if video_title was provided in the form, use it
                    video.title = form.cleaned_data['video_title']
                else: # Otherwise use the videos filename as the title.
                    video.title = vfile.name
            # Save the GlossVideo to get a primary key
            video.save()

            # Construct a filename for the video, because it doesn't have a path yet.
            vfile.name = GlossVideo.create_filename(gloss.idgloss, gloss.pk, video.pk, splitext(vfile.name)[1])
            video.videofile = vfile
            video.save()

            # TODO: provide some feedback that it worked (if immediate display of video isn't working)

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


addvideo_view = permission_required('video.add_glossvideo')(addvideo)


def addvideo_gloss(request):
    """Add a video from form and process the upload"""
    """View to present a video upload form and process the upload"""

    if request.method == 'POST':

        form = VideoUploadForGlossForm(request.POST, request.FILES)
        if form.is_valid():
            gloss_id = form.cleaned_data['gloss_id']
            gloss = get_object_or_404(Gloss, pk=gloss_id)
            vfile = form.cleaned_data['videofile']
            video = GlossVideo(gloss=gloss)

            video_title = form.cleaned_data['video_title']
            if vfile:  # If there is no video file, we don't want to create a glossvideo.
                if video_title:  # if video_title was provided in the form, use it
                    video.title = form.cleaned_data['video_title']
                else:  # Otherwise use the videos filename as the title.
                    video.title = vfile.name

            # Construct a filename for the video, because it doesn't have a path yet.
            vfile.name = GlossVideo.create_filename(gloss.idgloss, gloss.pk, video.pk, splitext(vfile.name)[1])
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


addvideo_gloss_view = permission_required('video.add_glossvideo')(addvideo_gloss)


def add_recorded_video_view(request):
    """Add video that is recorder in the interface."""
    if request.method == 'POST':
        # Load the data into the form
        form = VideoUploadForGlossForm(request.POST, request.FILES)
        if form.is_valid():
            gloss = get_object_or_404(Gloss, pk=form.cleaned_data['gloss_id'])
            vidfile = form.cleaned_data['videofile']
            if vidfile:
                glossvid = GlossVideo.objects.create(gloss=gloss, videofile=vidfile, dataset=gloss.dataset)
                # Return the created GlossVideos id/pk, so that it can be used to link to the uploaded video.
                return HttpResponse(json.dumps({'videoid': glossvid.pk}), content_type='application/json')


add_recorded_video_view = permission_required('video.add_glossvideo')(add_recorded_video_view)


def add_poster(request):
    """Process upload of poster file."""
    if request.method == 'POST':
        # Load the data into the form
        form = PosterUpload(request.POST)

        # Process the image data submitted as base64 encoded.
        img = form.data['posterfile']
        # Get rid of the preceding info before the filedata.
        format, imgstr = img.split(';base64,')
        # Get the file extension
        ext = format.split('/')[-1]
        # Load the base64 encoded data to a ContentFile.
        data = ContentFile(b64decode(imgstr), name='temp.' + ext)

        # Get glossvideos pk from the submitted form data
        glossvideo_pk = form.data['pk']
        glossvideo = GlossVideo.objects.get(pk=glossvideo_pk)
        # Delete the existing file (we do not want to keep copies of them).
        glossvideo.posterfile.delete()
        # Create a desired filename for the posterfile.
        data.name = glossvideo.create_poster_filename(ext)
        glossvideo.posterfile = data
        glossvideo.save()
    if 'HTTP_REFERER' in request.META:
        url = request.META['HTTP_REFERER']
    else:
        url = '/'
    return redirect(url)


add_poster_view = permission_required('video.change_glossvideo')(add_poster)


class AddVideosView(FormView):
    """View for multiple video file upload. These videos will have no connection to glosses."""
    form_class = MultipleVideoUploadForm
    template_name = 'addvideos.html'
    success_url = '/video/add/'

    def get_form(self, formclass=None):
        form = super(AddVideosView, self).get_form()
        allowed_datasets = get_objects_for_user(self.request.user, 'dictionary.view_dataset')
        # Make sure we only list datasets the user has permissions to.
        form.fields["dataset"].queryset = form.fields["dataset"].queryset.filter(id__in=[x.id for x in allowed_datasets])
        return form

    def post(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        files = request.FILES.getlist('file_field')
        if form.is_valid():
            data = form.cleaned_data
            dataset = data['dataset']
            for f in files:
                GlossVideo.objects.create(videofile=f, dataset=dataset, title=f.name)
            return self.form_valid(form)
        else:
            return self.form_invalid(form)


addvideos_formview = permission_required(['video.add_glossvideo', 'video.change_glossvideo'])(AddVideosView.as_view())


class UploadedGlossvideosListView(ListView):
    model = GlossVideo
    template_name = 'uploaded_glossvideos.html'
    paginate_by = 10
    context_object_name = 'videos'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(UploadedGlossvideosListView, self).get_context_data(**kwargs)
        page = self.request.GET.get('page')
        context['page'] = page
        # Set get params in form
        form = UpdateGlossVideoForm(self.request.GET)
        if 'dataset' in self.request.GET and self.request.GET.get('dataset'):
            # Set queryset for form.gloss
            form.fields["gloss"].queryset = Gloss.objects.filter(dataset__pk=self.request.GET.get("dataset"))
        else:
            # If there is no dataset set, list only glosses that have no dataset.
            form.fields["gloss"].queryset = Gloss.objects.filter(dataset__isnull=True)
        context['form'] = form
        return context

    def get_queryset(self):
        qs = GlossVideo.objects.filter(gloss=None)
        get = self.request.GET
        if 'dataset' in get and self.request.GET.get('dataset'):
            # Filter based on param dataset
            qs = qs.filter(dataset=get['dataset'])
        else:
            # If no dataset is selected, show only GlossVideos that don't have a dataset.
            qs = qs.filter(dataset__isnull=True)
        if 'page' in get:
            page = self.request.GET.get('page')
        else:
            page = 0
        return qs

    def render_to_response(self, context, **response_kwargs):
        return super(UploadedGlossvideosListView, self).render_to_response(context)


uploaded_glossvideos_listview = permission_required('video.change_glossvideo')(UploadedGlossvideosListView.as_view())


def update_glossvideo(request):
    """Here we process the post request for updating a glossvideo."""
    if request.is_ajax():
        # If request is AJAX, follow this procedure.
        if request.method == 'POST':
            data = json.loads(request.body)
            for item in data['updatelist']:
                if 'gloss' in item and 'glossvideo' in item:
                    glossvideo = GlossVideo.objects.get(pk=item['glossvideo'])
                    glossvideo.gloss = Gloss.objects.get(pk=item['gloss'])
                    glossvideo.save()
            if "ajax" in data and data["ajax"] == "true":
                # If the param 'ajax' is included, we received what we were supposed to, return OK.
                return HttpResponse("OK", status=200)
    else:
        # If not AJAX, we expect one form to be submitted.
        if request.method == 'POST':
            post = request.POST
            if 'gloss' in post and 'glossvideo' in post:
                glossvideo = GlossVideo.objects.get(pk=post['glossvideo'])
                glossvideo.gloss = Gloss.objects.get(pk=post['gloss'])
                glossvideo.save()
    if "HTTP_REFERER" in request.META:
        return redirect(request.META["HTTP_REFERER"])
    return redirect("/")


update_glossvideo_view = permission_required('video.change_glossvideo')(update_glossvideo)


def poster(request, videoid):
    """Generate a still frame for a video (if needed) and
    generate a redirect to the static server for this frame"""

    video = get_object_or_404(GlossVideo, pk=videoid)

    return redirect(video.poster_url())


poster_view = poster


def video(request, videoid):
    """Redirect to the video url for this videoid"""

    video = get_object_or_404(GlossVideo, pk=videoid)

    return redirect(video)

video_view = video


def change_glossvideo_order(request):
    """Moves selected glossvideos position within glosses glossvideos."""
    videoid = request.POST["videoid"]
    direction = request.POST["direction"]
    video = GlossVideo.objects.get(pk=videoid)
    videolist= list(GlossVideo.objects.filter(gloss=video.gloss).order_by('version'))
    index = videolist.index(video)

    # Set the new index based on the direction we want the move to happen to.
    if direction == "up":
        if index < 1:
            newindex = 0
        else:
            newindex = index-1
    if direction == "down":
        newindex = index+1

    try:
        # Move object: Insert object into newindex and remove it from old index.
        videolist.insert(newindex, videolist.pop(index))
        # Save the list indexes into the 'version' field of objects.
        for i, vid in enumerate(videolist):
            vid.version = i
            vid.save()
    except ValueError:
        # If index is out of lists range.
        pass
    except NameError:
        # In case 'direction' is not defined.
        pass

    referer = request.META.get("HTTP_REFERER")
    if "?edit" in referer:
        return redirect(referer)
    else:
        return redirect(request.META.get("HTTP_REFERER") + "?edit")


change_glossvideo_order_view = permission_required('video.change_glossvideo')(change_glossvideo_order)
