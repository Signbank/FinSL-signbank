# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
from django.contrib.auth.decorators import permission_required
from django.contrib import messages
from django.shortcuts import render
from django.db.models import Prefetch, Q
from django.db import connection
from django.urls import reverse
from django.core.mail import mail_admins
from django.utils.translation import gettext as _
from django.conf import settings

from signbank.dictionary.models import Gloss, Language, Translation, Keyword, Dataset
from signbank.video.models import GlossVideo, GlossVideoStorage


@permission_required("dictionary.search_gloss")
def infopage(request):
    context = dict()
    context["gloss_count"] = Gloss.objects.all().count()

    context["glossvideo_count"] = GlossVideo.objects.all().count()
    context["glosses_with_video"] = Gloss.objects.filter(glossvideo__isnull=False).count()
    context["glossless_video_count"] = GlossVideo.objects.filter(gloss__isnull=True).count()
    context["glossvideo_poster_count"] = GlossVideo.objects.exclude(Q(posterfile="") | Q(posterfile__isnull=True))\
        .count()
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
        dset["glosses_with_video"] = Gloss.objects.filter(dataset=d, glossvideo__isnull=False).count()
        dset["glossless_video_count"] = GlossVideo.objects.filter(gloss__isnull=True, dataset=d).count()
        dset["glossvideo_poster_count"] = GlossVideo.objects.filter(dataset=d).exclude(
            Q(posterfile="") | Q(posterfile__isnull=True)).count()
        dset["glossvideo_noposter_count"] = dset["glossvideo_count"] - dset["glossvideo_poster_count"]

        dset["translations"] = list()
        for language in d.translation_languages.all().prefetch_related(
                Prefetch("translation_set", queryset=Translation.objects.filter(gloss__dataset=d))):
            dset["translations"].append([language, language.translation_set.count()])
        datasets_context.append(dset)

    # For users that are 'staff'.
    if getattr(settings, "FEAT_INFO_MISSING_FILES", False) is True and request.user.is_staff:
        # Find missing files
        problems = list()
        storage = GlossVideoStorage()
        for vid in GlossVideo.objects.all():
            if vid.videofile and not storage.exists(vid.videofile.name):
                problems.append({"id": vid.id, "file": vid.videofile, "type": "video", "url": vid.get_absolute_url()})
            if vid.posterfile and not storage.exists(vid.posterfile.name):
                problems.append({"id": vid.id, "file": vid.posterfile, "type": "poster",
                                 "admin_url": reverse("admin:video_glossvideo_change", args=(vid.id,))})
        context["problems"] = problems

    return render(request, "../templates/infopage.html",
                  {'context': context,
                   'datasets': datasets_context,
                   })
