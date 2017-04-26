from django.shortcuts import render, redirect, get_object_or_404
from django.forms import ModelForm
from django.forms.models import model_to_dict
from django.http import HttpResponseForbidden
from django.utils.translation import ugettext_lazy as _
from django_comments.models import Comment
from django_comments.forms import CommentForm


def edit_comment(request, id):
    """View to bind comment data to form and update comment."""
    comment = get_object_or_404(Comment, id=id)
    # Make sure that only the commenter can edit the comment.
    if not request.user == comment.user:
        return HttpResponseForbidden(_("You are not allowed to edit this comment, "
                                       "because you are not the author of the comment."))
    if request.method == 'POST':
        form = EditCommentForm(request.POST)
        if form.is_valid():
            comment.comment = form.cleaned_data["comment"]
            comment.save()
        if 'HTTP_REFERER' in request.META:
            return redirect(request.META['HTTP_REFERER'])
        else:
            return redirect(request.path)

    else:
        return bind_comment(request, comment)


def bind_comment(request, comment):
    """Bind the data into the form."""
    commdict = model_to_dict(comment)
    form = CommentForm(comment, commdict)
    return render(request, 'comments/edit_comment.html', {'form': form})


class EditCommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ['comment']

