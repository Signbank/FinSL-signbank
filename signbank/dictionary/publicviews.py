# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.db.models import Q, Prefetch
from django.db.models.functions import Substr, Upper
from django.templatetags.static import static
from django.utils.translation import ugettext as _
from django.views.decorators.cache import cache_page
from django.shortcuts import get_object_or_404

from .models import Gloss, Dataset, SignLanguage, GlossRelation, Translation, GlossTranslations
from ..video.models import GlossVideo
from .forms import GlossPublicSearchForm
from .adminviews import serialize_glosses


class GlossListPublicView(ListView):
    model = Gloss
    template_name = 'dictionary/public_gloss_list.html'
    paginate_by = 20

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(GlossListPublicView, self).get_context_data(**kwargs)
        context["searchform"] = GlossPublicSearchForm(self.request.GET)
        context["signlanguages"] = SignLanguage.objects.filter(dataset__is_public=True).distinct()
        context["signlanguage_count"] = context["signlanguages"].count()
        context["lang"] = self.request.GET.get("lang")
        if context["lang"]:
            context["searchform"].fields["dataset"].queryset = context["searchform"].fields["dataset"].queryset.filter(signlanguage__language_code_3char=context["lang"])
        context["datasets"] = self.request.GET.getlist("dataset")
        context["first_letters"] = Gloss.objects.filter(dataset__is_public=True, published=True)\
            .annotate(first_letters=Substr(Upper('idgloss'), 1, 1)).order_by('first_letters')\
            .values_list('first_letters').distinct()
        context['lexicons'] = Dataset.objects.filter(is_public=True)
        return context

    def get_queryset(self):
        # Get queryset
        qs = super(GlossListPublicView, self).get_queryset()
        get = self.request.GET

        # Exclude datasets that are not public.
        qs = qs.exclude(dataset__is_public=False)
        # Exclude glosses that are not 'published'.
        qs = qs.exclude(published=False)

        if 'lang' in get and get['lang'] != '' and get['lang'] != 'all':
            signlang = get.get('lang')
            qs = qs.filter(dataset__signlanguage__language_code_3char=signlang)

        # Search for multiple datasets (if provided)
        vals = get.getlist('dataset', [])
        if vals != []:
            qs = qs.filter(dataset__in=vals)

        if 'gloss' in get and get['gloss'] != '':
            val = get['gloss']
            # Filters
            qs = qs.filter(Q(idgloss__istartswith=val))
        if 'keyword' in get and get['keyword'] != '':
            val = get['keyword']
            # Filters
            qs = qs.filter(translation__keyword__text__istartswith=val)

        qs = qs.distinct()

        # Set order according to GET field 'order'
        if 'order' in get:
            qs = qs.order_by(get['order'])
        else:
            qs = qs.order_by('idgloss')

        qs = qs.select_related('dataset')
        # Prefetching translation and dataset objects for glosses to minimize the amount of database queries.
        qs = qs.prefetch_related(Prefetch('glosstranslations_set'),
                                 Prefetch('glosstranslations_set__language'),
                                 # Make sure we only show GlossVideos that have 'is_public=True'
                                 Prefetch('glossvideo_set', queryset=GlossVideo.objects.filter(is_public=True)))
        return qs


class GlossDetailPublicView(DetailView):
    model = Gloss
    template_name = 'dictionary/public_gloss_detail.html'
    context_object_name = 'gloss'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(GlossDetailPublicView, self).get_context_data(**kwargs)
        gloss = context["gloss"]
        context['translation_languages_and_translations'] = gloss.get_translations_for_translation_languages()
        # GlossRelations for this gloss
        context['glossrelations'] = GlossRelation.objects.filter(source=gloss)
        context['glossrelations_reverse'] = GlossRelation.objects.filter(target=gloss)

        # Create a meta description for the gloss.
        context["metadesc"] = "{glosstxt}: {idgloss} [{lexicon}] / ".format(
            glosstxt=_("Gloss"), idgloss=gloss, lexicon=gloss.dataset.public_name)
        for x in context['translation_languages_and_translations']:
            if x[1]:  # Show language name only if it has translations.
                context["metadesc"] += "{lang}: {trans} / ".format(lang=str(x[0]), trans=str(x[1]))
        context["metadesc"] += "{langtxt}: {lang} / {videotxt}: {videocount} / {notestxt}: {notes}".format(
            langtxt=_("Sign language"), lang=gloss.dataset.signlanguage, videotxt=_("Videos"),
            videocount=gloss.glossvideo_set.all().count(), notestxt=_("Notes"), notes=gloss.notes)
        try:
            context["first_video"] = gloss.glossvideo_set.first()
        except (AttributeError, ValueError):
            context["first_video"] = None
        # Create og:image url for the gloss if the first glossvideo has a posterfile.
        try:
            context["ogimage"] = context["first_video"].posterfile.url
        except (AttributeError, ValueError):
            context["ogimage"] = static('img/signbank_logo_ympyra1_sininen-compressor.png')

        return context

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.filter(published=True)
        # Make sure we only show GlossVideos that have 'is_public=True'
        return qs.prefetch_related(Prefetch('glossvideo_set', queryset=GlossVideo.objects.filter(is_public=True)))


@cache_page(60 * 15)
def public_gloss_list_xml(self, dataset_id):
    """Return ELAN schema valid XML of public glosses and their translations."""
    # http://www.mpi.nl/tools/elan/EAFv2.8.xsd
    dataset = get_object_or_404(Dataset, id=dataset_id, is_public=True)

    return serialize_glosses(dataset, Gloss.objects.filter(
        dataset=dataset, published=True, exclude_from_ecv=False).prefetch_related(
        Prefetch('translation_set', queryset=Translation.objects.filter(gloss__dataset=dataset)
                 .select_related('keyword', 'language')),
        Prefetch('glosstranslations_set', queryset=GlossTranslations.objects
                 .filter(gloss__dataset=dataset).select_related('language')))
                             )
