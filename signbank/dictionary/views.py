# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth.decorators import permission_required
from django.contrib.admin.views.decorators import user_passes_test
from django.core.exceptions import PermissionDenied
from django.utils.translation import ugettext as _

from tagging.models import Tag
from guardian.shortcuts import get_perms, get_objects_for_user
from .models import Dataset, Keyword, FieldChoice
from .forms import GlossCreateForm
from ..video.views import upload_glossvideo


@permission_required('dictionary.add_gloss')
def create_gloss(request):
    """Handle Gloss creation."""
    if request.method == 'POST':
        form = GlossCreateForm(request.POST, request.FILES)
        if form.is_valid():
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
            redirecturl = '/dictionary/gloss/' + str(new_gloss.pk) + '/?edit'
            upload_glossvideo(request, new_gloss.pk, redirecturl)

            return HttpResponseRedirect(redirecturl)
    else:
        allowed_datasets = get_objects_for_user(request.user, 'dictionary.view_dataset')
        form = GlossCreateForm()
        form.fields["dataset"].queryset = Dataset.objects.filter(id__in=[x.id for x in allowed_datasets])
        return render(request, 'dictionary/create_gloss.html', {'form': form})


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
    return HttpResponse('OK')


