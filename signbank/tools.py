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
from django.utils.translation import ugettext as _
from django.conf import settings

from signbank.dictionary.models import Gloss, Language, Translation, Keyword, Dataset, GlossRelation
from signbank.video.models import GlossVideo


@permission_required("dictionary.search_gloss")
def infopage(request):
    context = dict()
    context["gloss_count"] = Gloss.objects.all().count()

    context["glossvideo_count"] = GlossVideo.objects.all().count()
    context["glosses_with_video"] = GlossVideo.objects.filter(gloss__isnull=False).order_by("gloss_id")\
        .distinct("gloss_id").count()
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
        dset["glosses_with_video"] = GlossVideo.objects.filter(gloss__isnull=False, gloss__dataset=d)\
            .order_by("gloss_id").distinct("gloss_id").count()
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
    if request.user.is_staff:
        # Find missing files
        problems = list()
        for vid in GlossVideo.objects.all():
            if vid.videofile and not os.path.isfile(vid.videofile.path):
                problems.append({"id": vid.id, "file": vid.videofile, "type": "video", "url": vid.get_absolute_url()})
            if vid.posterfile and not os.path.isfile(vid.posterfile.path):
                problems.append({"id": vid.id, "file": vid.posterfile, "type": "poster",
                                 "admin_url": reverse("admin:video_glossvideo_change", args=(vid.id,))})
        context["problems"] = problems

        # Only do this if the database is postgresql.
        if settings.DB_IS_PSQL:
            # Get postgresql database size and calculate usage percentage.
            with connection.cursor() as cursor:
                cursor.execute("SELECT pg_database_size(%s)", [settings.PSQL_DB_NAME])
                psql_db_size = cursor.fetchone()[0]
                cursor.execute("SELECT pg_size_pretty(pg_database_size(%s))", [settings.PSQL_DB_NAME])
                psql_db_size_pretty = cursor.fetchone()[0]
            context["psql_db_size"] = psql_db_size
            context["psql_db_size_pretty"] = psql_db_size_pretty
            # Calculate the usage percentage.
            usage_percentage = round((psql_db_size / settings.PSQL_DB_QUOTA)*100, 2)
            # Convert to str, so django localization doesn't change dot delimiter to comma in different languages.
            context["psql_db_usage"] = str(usage_percentage)
            if usage_percentage >= 80.0:
                messages.error(request, _("Database storage space usage is high, be prepared increase database quota. "
                                          "If the database gets over the quota maximum, data will be lost!"))
            if usage_percentage >= 95.0:
                mail_admins(subject="Database is reaching maximum quota!",
                            message="Dear admin, you are receiving this message because the database "
                                    "is reaching its maximum quota. "
                                    "Current size of the database is %s and the usage percentage is %s%%." %
                                    (str(psql_db_size_pretty), str(usage_percentage)))

    return render(request, "../templates/infopage.html",
                  {'context': context,
                   'datasets': datasets_context,
                   })
