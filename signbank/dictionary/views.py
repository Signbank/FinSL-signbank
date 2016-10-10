import csv

from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models.fields import NullBooleanField

from signbank.dictionary.forms import *
from signbank.feedback.models import *
from signbank.dictionary.update import update_keywords
import forms
from signbank.tools import video_to_signbank, compare_valuedict_to_gloss
from django.contrib.admin.views.decorators import user_passes_test

from django.utils.translation import ugettext_lazy as _


def keyword_value_list(request, prefix=None):
    """View to generate a list of possible values for a keyword given a prefix."""

    kwds = Keyword.objects.filter(text__startswith=prefix)
    kwds_list = [k.text for k in kwds]
    return HttpResponse("\n".join(kwds_list), content_type='text/plain')


@user_passes_test(lambda u: u.is_staff, login_url='/accounts/login/')
def try_code(request):
    """A view for the developer to try out things"""

    choicedict = {}

    for key, choices in choicedict.items():

        for machine_value, english_name in choices:
            FieldChoice(
                english_name=english_name, field=key, machine_value=machine_value).save()

    return HttpResponse('OK')


@login_required
def add_new_sign(request):
    return render(request, 'dictionary/add_gloss.html', {'add_gloss_form': GlossCreateForm()})


@login_required
def import_csv(request):
    if not request.user.is_staff and len(request.user.groups.filter(name="Publisher")) == 0:
        # Translators: import_csv: not allowed to see requested page (Might not be useful to translate)
        return HttpResponse(_('You are not allowed to see this page.'))

    uploadform = forms.CSVUploadForm
    changes = []

    # Propose changes
    if len(request.FILES) > 0:

        changes = []
        csv_lines = request.FILES['file'].read().split('\n')

        for nl, line in enumerate(csv_lines):

            # The first line contains the keys
            if nl == 0:
                keys = line.strip().split(',')
                continue
            elif len(line) == 0:
                continue

            values = csv.reader([line]).next()
            value_dict = {}

            for nv, value in enumerate(values):

                try:
                    value_dict[keys[nv]] = value
                except IndexError:
                    pass

            try:
                pk = int(value_dict['Signbank ID'])
            except ValueError:
                continue

            gloss = Gloss.objects.get(pk=pk)

            changes += compare_valuedict_to_gloss(value_dict, gloss)

        stage = 1

    # Do changes
    elif len(request.POST) > 0:

        for key, new_value in request.POST.items():

            try:
                pk, fieldname = key.split('.')

            # In case there's no dot, this is not a value we set at the
            # previous page
            except ValueError:
                continue

            gloss = Gloss.objects.get(pk=pk)

            # Updating the keywords is a special procedure, because it has
            # relations to other parts of the database
            if fieldname == 'Keywords':
                update_keywords(gloss, None, new_value)
                gloss.save()
                continue

            # Replace the value for bools
            if isinstance(gloss._meta.get_field(fieldname), NullBooleanField):

                if new_value in ['true', 'True']:
                    new_value = True
                else:
                    new_value = False

            # The normal change and save procedure
            setattr(gloss, fieldname, new_value)
            gloss.save()

        stage = 2

    # Show uploadform
    else:

        stage = 0
    return render(request, 'dictionary/import_csv.html', {'form': uploadform, 'stage': stage, 'changes': changes})
