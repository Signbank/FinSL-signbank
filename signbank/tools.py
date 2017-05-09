from settings.production import WSGI_FILE
import os
import shutil
from HTMLParser import HTMLParser
from django.contrib.admin.views.decorators import user_passes_test
from django.contrib.auth.decorators import permission_required
from django.shortcuts import render
from django.db.models import Prefetch, Q
from django.urls import reverse

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
def unescape(string):
    return HTMLParser().unescape(string)


@user_passes_test(lambda u: u.is_staff, login_url='/accounts/login/')
def compare_valuedict_to_gloss(valuedict, gloss):
    """Takes a dict of arbitrary key-value pairs, and compares them to a gloss"""

    # Create an overview of all fields, sorted by their human name
    fields = {field.verbose_name: field for field in gloss._meta.fields}

    differences = []

    # Go through all values in the value dict, looking for differences with
    # the gloss
    for human_key, new_human_value in valuedict.items():

        # If these are not fields, but relations to other parts of the
        # database, go look for differenes elsewhere
        if human_key == 'Keywords':

            current_keyword_string = str(', '.join([translation.translation.text.encode(
                'utf-8') for translation in gloss.translation_set.all()]))

            if current_keyword_string != new_human_value:
                differences.append({'pk': gloss.pk,
                                    'idgloss': gloss.idgloss,
                                    'machine_key': human_key,
                                    'human_key': human_key,
                                    'original_machine_value': current_keyword_string,
                                    'original_human_value': current_keyword_string,
                                    'new_machine_value': new_human_value,
                                    'new_human_value': new_human_value})

        # If not, find the matching field in the gloss, and remember its 'real'
        # name
        try:
            field = fields[human_key]
            machine_key = field.name
        except KeyError:
            continue

        # Try to translate the value to machine values if needed
        if len(field.choices) > 0:
            human_to_machine_values = {
                human_value: machine_value for machine_value, human_value in field.choices}

            try:
                new_machine_value = human_to_machine_values[new_human_value]
            except KeyError:
                if new_human_value in ['', ' ']:
                    new_human_value = 'None'
                    new_machine_value = None

        elif field.__class__.__name__ == 'IntegerField':

            try:
                new_machine_value = int(new_human_value)
            except ValueError:
                new_human_value = 'None'
                new_machine_value = None
        elif field.__class__.__name__ == 'NullBooleanField':

            if new_human_value in ['True', 'true']:
                new_machine_value = True
            else:
                new_machine_value = False

        else:
            if new_human_value == 'None':
                new_machine_value = None
            else:
                new_machine_value = new_human_value

        # Try to translate the key to machine keys if possible
        try:
            original_machine_value = getattr(gloss, machine_key)
        except KeyError:
            continue

        # Translate back the machine value from the gloss
        try:
            original_human_value = dict(field.choices)[original_machine_value]
        except KeyError:
            original_human_value = original_machine_value

        # Remove any weird char
        try:
            new_machine_value = unescape(new_machine_value)
            new_human_value = unescape(new_human_value)
        except TypeError:
            pass

        # Check for change, and save your findings if there is one
        if original_machine_value != new_machine_value:
            differences.append({'pk': gloss.pk,
                                'idgloss': gloss.idgloss,
                                'machine_key': machine_key,
                                'human_key': human_key,
                                'original_machine_value': original_machine_value,
                                'original_human_value': original_human_value,
                                'new_machine_value': new_machine_value,
                                'new_human_value': new_human_value})

    return differences


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
        from settings.development import MEDIA_ROOT
        for vid in GlossVideo.objects.all():
            if vid.videofile != "" and not os.path.isfile(MEDIA_ROOT + str(vid.videofile)):
                problems.append({"id": vid.id, "file": vid.videofile, "type": "video", "url": vid.get_absolute_url()})
            if vid.posterfile != "" and not os.path.isfile(MEDIA_ROOT + str(vid.posterfile)):
                problems.append({"id": vid.id, "file": vid.posterfile, "type": "poster", "admin_url": reverse("admin:glossvideo_change", args=(vid.id,))})
        context["problems"] = problems

    return render(request, "../templates/infopage.html",
                  {'context': context,
                   'datasets': datasets_context,
                   })
