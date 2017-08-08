from __future__ import unicode_literals
from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth.decorators import permission_required

from signbank.dictionary.forms import *
from signbank.dictionary.update import update_keywords
from .models import Keyword
from .forms import *
from django.contrib.admin.views.decorators import user_passes_test

from django.utils.translation import ugettext_lazy as _
from guardian.shortcuts import get_objects_for_user


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


@permission_required('dictionary.add_gloss')
def add_new_sign(request):
    allowed_datasets = get_objects_for_user(request.user, 'dictionary.view_dataset')
    form = GlossCreateForm()
    form.fields["dataset"].queryset = Dataset.objects.filter(id__in=[x.id for x in allowed_datasets])
    return render(request, 'dictionary/add_gloss.html', {'add_gloss_form': form})