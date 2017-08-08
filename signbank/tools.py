from __future__ import unicode_literals
from .settings.production import WSGI_FILE
import os
import shutil
from django.contrib.admin.views.decorators import user_passes_test
from django.contrib.auth.decorators import permission_required
from django.shortcuts import render
from django.db.models import Prefetch, Q
from django.urls import reverse
from .settings.production import MEDIA_ROOT

# ==========================
# Constants
# ==========================

ROOT = '/var/www2/signbank/live/'
SB_VIDEO_FOLDER = ROOT + 'writable/glossvideo/'


# ==========================
# Functions
# ==========================

@user_passes_test(lambda u: u.is_staff, login_url='/accounts/login/')
def video_to_signbank(source_folder, gloss, extension):
    # Add a dot before the extension if needed
    if extension[0] != '.':
        extension = '.' + extension

    # Figure out some names
    annotation_id = gloss.idgloss_en
    pk = str(gloss.pk)
    destination_folder = SB_VIDEO_FOLDER + annotation_id[:2] + '/'

    # Create the necessary subfolder if needed
    if not os.path.isdir(destination_folder):
        os.mkdir(destination_folder)

    # Move the file
    source = source_folder + annotation_id + extension
    goal = destination_folder + annotation_id + '-' + pk + extension

    if os.path.isfile(goal):
        overwritten = True
    else:
        overwritten = False

    try:
        shutil.copy(source, goal)
        was_allowed = True
    except IOError:
        was_allowed = False

    os.remove(source)

    return overwritten, was_allowed


@user_passes_test(lambda u: u.is_staff, login_url='/accounts/login/')
def reload_signbank(request=None):
    """Functions to clear the cache of Apache, also works as view"""

    # Refresh the wsgi script
    os.utime(WSGI_FILE, None)

    # If this is an HTTP request, give an HTTP response
    if request is not None:
        # Javascript to reload the page three times
        js = """<script>
        xmlHttp = new XMLHttpRequest();
        xmlHttp.open( "GET", 'http://signbank.csc.fi', false );
        xmlHttp.send( null );
        xmlHttp = new XMLHttpRequest();
        xmlHttp.open( "GET", 'http://signbank.csc.fi', false );
        xmlHttp.send( null );
        </script>OK"""

        from django.http import HttpResponse

        return HttpResponse(js)


@user_passes_test(lambda u: u.is_staff, login_url='/accounts/login/')
def refresh_videofilenames(request=None):
    from django.core.management import call_command
    call_command('refresh_videofilenames', verbosity=3, interactive=False)
    from django.http import HttpResponse

    return HttpResponse("Done refreshing video filenames.")


@permission_required("dictionary.search_gloss")
def infopage(request):
    from signbank.dictionary.models import Gloss, Language, Translation, Keyword, Dataset
    from signbank.video.models import GlossVideo
    context = dict()
    context["gloss_count"] = Gloss.objects.all().count()

    context["glossvideo_count"] = GlossVideo.objects.all().count()
    context["glosses_with_video"] = GlossVideo.objects.filter(gloss__isnull=False).order_by("gloss_id")\
        .distinct("gloss_id").count()
    context["glossless_video_count"] = GlossVideo.objects.filter(gloss__isnull=True).count()
    context["glossvideo_poster_count"] = GlossVideo.objects.exclude(Q(posterfile="") | Q(posterfile__isnull=True)).count()
    context["glossvideo_noposter_count"] = context["glossvideo_count"] - context["glossvideo_poster_count"]

    context["languages"] = Language.objects.all().prefetch_related("translation_set")
    context["keyword_count"] = Keyword.objects.all().count()

    datasets_context = list()
    datasets = Dataset.objects.all().prefetch_related("gloss_set", "translation_languages")
    for d in datasets:
        dset = dict()
        dset["dataset"] = d
        dset["gloss_count"] = Gloss.objects.filter(dataset=d).count()

        dset["glossvideo_count"] = GlossVideo.objects.filter(gloss__dataset=d).count()
        dset["glosses_with_video"] = GlossVideo.objects.filter(gloss__isnull=False, gloss__dataset=d).order_by("gloss_id")\
            .distinct("gloss_id").count()
        dset["glossless_video_count"] = GlossVideo.objects.filter(gloss__isnull=True, dataset=d).count()
        dset["glossvideo_poster_count"] = GlossVideo.objects.filter(dataset=d).exclude(
            Q(posterfile="") | Q(posterfile__isnull=True)).count()
        dset["glossvideo_noposter_count"] = dset["glossvideo_count"] - dset["glossvideo_poster_count"]

        dset["translations"] = list()
        for language in d.translation_languages.all().prefetch_related(
                Prefetch("translation_set", queryset=Translation.objects.filter(gloss__dataset=d))):
            dset["translations"].append([language, language.translation_set.count()])
        datasets_context.append(dset)

    # Find missing files for users that are 'staff'.
    if request.user.is_staff:
        problems = list()
        for vid in GlossVideo.objects.all():
            if vid.videofile != "" and not os.path.isfile(MEDIA_ROOT + vid.videofile.path):
                problems.append({"id": vid.id, "file": vid.videofile, "type": "video", "url": vid.get_absolute_url()})
            if vid.posterfile != "" and not os.path.isfile(MEDIA_ROOT + str(vid.posterfile)):
                problems.append({"id": vid.id, "file": vid.posterfile, "type": "poster", "admin_url": reverse("admin:video_glossvideo_change", args=(vid.id,))})
        context["problems"] = problems

    return render(request, "../templates/infopage.html",
                  {'context': context,
                   'datasets': datasets_context,
                   })
