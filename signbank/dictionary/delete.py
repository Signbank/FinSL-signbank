from django.contrib.auth.decorators import permission_required
from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.utils.translation import ugettext as _
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseNotAllowed

from guardian.shortcuts import get_perms

from .models import GlossURL


@permission_required('dictionary.delete_glossurl')
def glossurl(request, glossurl):
    if request.method == 'POST':
        glossurl = get_object_or_404(GlossURL, id=glossurl)
        if 'view_dataset' not in get_perms(request.user, glossurl.gloss.dataset):
            # If user has no permissions to dataset, raise PermissionDenied to show 403 template.
            msg = _("You do not have permissions to add tags to glosses of this lexicon.")
            messages.error(request, msg)
            raise PermissionDenied(msg)
        glossurl_id = glossurl.id
        try:
            glossurl.delete()
        except PermissionDenied:
            return HttpResponseForbidden('Permission Denied: Unable to delete GlossURL(id): ' + str(glossurl.id),
                                         content_type='text/plain')
        return HttpResponse('Deleted GlossURL(id): ' + str(glossurl_id), content_type='text/plain')
    else:
        return HttpResponseForbidden('Must be POST.')
