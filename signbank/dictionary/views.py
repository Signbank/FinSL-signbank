# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth.decorators import permission_required
from django.contrib.admin.views.decorators import user_passes_test
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import PermissionDenied
from django.urls import reverse, reverse_lazy
from django.utils.translation import ugettext as _
from django.views.generic.list import ListView
from django.views.generic import FormView
from django.db.models import Q, F, Count, Case, Value, When, BooleanField

from tagging.models import Tag
from guardian.shortcuts import get_perms, get_objects_for_user, get_users_with_perms
from notifications.signals import notify

from .models import Dataset, Keyword, FieldChoice, Gloss, GlossRelation
from .forms import GlossCreateForm, LexiconForm
from ..video.forms import GlossVideoForm


@permission_required('dictionary.add_gloss')
def create_gloss(request):
    """Handle Gloss creation."""
    if request.method == 'POST':
        form = GlossCreateForm(request.POST)
        glossvideoform = GlossVideoForm(request.POST, request.FILES)
        glossvideoform.fields['videofile'].required=False
        if form.is_valid() and glossvideoform.is_valid():
            if 'view_dataset' not in get_perms(request.user, form.cleaned_data["dataset"]):
                # If user has no permissions to dataset, raise PermissionDenied to show 403 template.
                msg = _("You do not have permissions to create glosses for this lexicon.")
                messages.error(request, msg)
                raise PermissionDenied(msg)

            new_gloss = form.save(commit=False)
            new_gloss.created_by = request.user
            new_gloss.updated_by = request.user
            new_gloss.save()
            if form.cleaned_data["tag"]:
                Tag.objects.add_tag(new_gloss, form.cleaned_data["tag"].name)
            if glossvideoform.cleaned_data['videofile']:
                glossvideo = glossvideoform.save(commit=False)
                glossvideo.gloss = new_gloss
                glossvideo.save()
            return HttpResponseRedirect(reverse('dictionary:admin_gloss_view', kwargs={'pk': new_gloss.pk}))

        else:
            # Return bound fields with errors if the form is not valid.
            allowed_datasets = get_objects_for_user(request.user, 'dictionary.view_dataset')
            form.fields["dataset"].queryset = Dataset.objects.filter(id__in=[x.id for x in allowed_datasets])
            return render(request, 'dictionary/create_gloss.html', {'form': form, 'glossvideoform': glossvideoform})
    else:
        allowed_datasets = get_objects_for_user(request.user, 'dictionary.view_dataset')
        form = GlossCreateForm()
        glossvideoform = GlossVideoForm()
        form.fields["dataset"].queryset = Dataset.objects.filter(id__in=[x.id for x in allowed_datasets])
        return render(request, 'dictionary/create_gloss.html', {'form': form, 'glossvideoform': glossvideoform})


def keyword_value_list(request, prefix=None):
    """View to generate a list of possible values for a keyword given a prefix."""
    kwds = Keyword.objects.filter(text__startswith=prefix)
    kwds_list = [k.text for k in kwds]
    return HttpResponse("\n".join(kwds_list), content_type='text/plain')


@user_passes_test(lambda u: u.is_staff, login_url='/accounts/login/')
def try_code(request):
    """A view for the developer to try out things"""
    choicedict = {}
    for key, choices in list(choicedict.items()):
        for machine_value, english_name in choices:
            FieldChoice(
                english_name=english_name, field=key, machine_value=machine_value).save()
    return HttpResponse('OK', status=200)


class ManageLexiconsListView(ListView):
    model = Dataset
    template_name = 'dictionary/manage_lexicons.html'
    paginate_by = 50

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        qs = self.get_queryset()
        context['has_permissions'] = qs.filter(has_view_perm=True)
        context['no_permissions'] = qs.filter(has_view_perm=False)
        current_site = get_current_site(self.request)
        context['current_site_domain'] = getattr(current_site, 'domain', self.request.get_host())
        # Show users with permissions to lexicons to SuperUsers
        if self.request.user.is_superuser:
            for lexicon in context['has_permissions']:
                lexicon.users_with_perms = get_users_with_perms(obj=lexicon, with_superusers=True)
            for lexicon in context['no_permissions']:
                lexicon.users_with_perms = get_users_with_perms(obj=lexicon, with_superusers=True)
        return context

    def get_queryset(self):
        # Get allowed datasets for user (django-guardian)
        allowed_datasets = get_objects_for_user(self.request.user, 'dictionary.view_dataset')
        # Get queryset
        qs = super().get_queryset()
        qs = qs.annotate(
            has_view_perm=Case(
                When(Q(id__in=allowed_datasets), then=Value(True)),
                default=Value(False), output_field=BooleanField()))
        qs = qs.select_related('signlanguage')
        return qs


class ApplyLexiconPermissionsFormView(FormView):
    form_class = LexiconForm
    template_name = 'dictionary/manage_lexicons.html'
    success_url = reverse_lazy('dictionary:manage_lexicons')

    def form_valid(self, form):
        dataset = form.cleaned_data['dataset']
        admins = dataset.admins.all()
        notify.send(sender=self.request.user, recipient=admins,
                    verb="{txt} {dataset}".format(txt=_("applied for permissions to:"), dataset=dataset.public_name),
                    action_object=self.request.user,
                    description="{user} ({user.first_name} {user.last_name}) {txt} {dataset}".format(
                        user=self.request.user, txt=_("applied for permissions to lexicon:"),
                        dataset=dataset.public_name
                    ),
                    target=self.request.user, public=False)
        msg = "{text} {lexicon_name}".format(text=_("Successfully applied permissions for"), lexicon_name=dataset.public_name)
        messages.success(self.request, msg)
        return super().form_valid(form)


def network_graph(request):
    """Network graph of GlossRelations"""
    context = dict()
    form = LexiconForm(request.GET, use_required_attribute=False)
    # Get allowed datasets for user (django-guardian)
    allowed_datasets = get_objects_for_user(request.user, 'dictionary.view_dataset')
    # Filter the forms dataset field for the datasets user has permission to.
    form.fields["dataset"].queryset = Dataset.objects.filter(id__in=[x.id for x in allowed_datasets])
    dataset = None
    if form.is_valid():
        form.fields["dataset"].widget.is_required = False
        dataset = form.cleaned_data["dataset"]

    if dataset:
        context["dataset"] = dataset
        nodeqs = Gloss.objects.filter(Q(dataset=dataset),
                                      Q(glossrelation_target__isnull=False) | Q(glossrelation_source__isnull=False))\
            .distinct().values("id").annotate(label=F("idgloss"), size=Count("glossrelation_source")+Count("glossrelation_target"))
        context["nodes"] = json.dumps(list(nodeqs))
        edgeqs = GlossRelation.objects.filter(Q(source__dataset=dataset) | Q(target__dataset=dataset)).values("id", "source", "target")
        context["edges"] = json.dumps(list(edgeqs))
    return render(request, "dictionary/network_graph.html",
                  {'context': context,
                   'form': form
                   })
