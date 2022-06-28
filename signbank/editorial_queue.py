from .dictionary.models import Gloss
from django.shortcuts import render
from django_comments import get_model as django_comments_get_model


def get_queue_items(request):
    """
        As per the first comment of N2-92, get the glosses which are assigned to you
        """
    user = request.user
    glosses = Gloss.objects.filter(assigned_user=user)
    gloss_data = []
    for gloss in glosses:
        comments = django_comments_get_model().objects.filter(
            object_pk=str(gloss.id),
            is_removed=False,
        ).order_by('-submit_date')[:3]
        gloss_data.append({
            'gloss': gloss,
            'comments': comments
        })

    if 'details/' in request.path:
        template = 'editorial_queue/queue_gloss_details.html'
    else:
        template = 'editorial_queue/queue.html'

    return render(request, template, {'glosses': gloss_data})
