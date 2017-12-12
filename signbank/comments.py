# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import re

from django import forms
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic.list import ListView
from django.forms import ModelForm
from django.forms.models import model_to_dict
from django.http import HttpResponseForbidden
from django.utils.translation import ugettext as _
from django.utils.translation import ugettext_lazy as _lazy
from django.contrib.sites.shortcuts import get_current_site
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.db.utils import OperationalError
from django.contrib.auth.models import User

from tagging.models import Tag, TaggedItem
from guardian.shortcuts import get_objects_for_user
from django_comments.models import Comment
from django_comments.signals import comment_was_posted
from django_comments.forms import CommentForm
from django_comments import get_model as django_comments_get_model
from django_comments.admin import CommentsAdmin
from notifications.signals import notify

from .dictionary.models import AllowedTags
from .dictionary.admin import TagAdminInline, TagListFilter


class CommentTagForm(forms.Form):
    """Form for tags, meant to be used when adding tags to Comments."""
    try:
        qs = AllowedTags.objects.get(content_type=ContentType.objects.get_for_model(Comment)).allowed_tags.all()
    except (ObjectDoesNotExist, OperationalError):
        qs = Tag.objects.all()
    tag = forms.ModelChoiceField(queryset=qs, required=False, empty_label="---", to_field_name='name',
                                 widget=forms.Select(attrs={'class': 'form-control'}), label=_lazy('Tag'))


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
            if form.cleaned_data["tag"]:
                tag = form.cleaned_data["tag"]
                Tag.objects.add_tag(comment, tag)
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
    tagform = CommentTagForm
    return render(request, 'comments/edit_comment.html', {'form': form, 'tagform': tagform})


class EditCommentForm(ModelForm):
    try:
        qs = AllowedTags.objects.get(content_type=ContentType.objects.get_for_model(Comment)).allowed_tags.all()
    except (ObjectDoesNotExist, OperationalError):
        qs = Tag.objects.all()
    tag = forms.ModelChoiceField(queryset=qs, required=False, empty_label="---", to_field_name='name',
                                 widget=forms.Select(attrs={'class': 'form-control'}), label=_lazy('Tag'))

    class Meta:
        model = Comment
        fields = ['comment']


def latest_comments_page(request, count=20):
    count = int(count)
    if count > 100:
        count = 100
    qs = django_comments_get_model().objects.filter(
        site__pk=get_current_site(request).pk,
        is_public=True,
        is_removed=False,
    ).order_by('-submit_date')[:count]
    return render(request, 'comments/latest_comments_page.html', {'comments': qs})


def latest_comments(request):
    qs = django_comments_get_model().objects.filter(
        site__pk=get_current_site(request).pk,
        is_public=True,
        is_removed=False,
    ).order_by('-submit_date')[:10]
    return render(request, 'comments/latest_comments.html', {'comments': qs})


class CommentListView(ListView):
    model = Comment
    template_name = 'comments/search_comments.html'
    paginate_by = 20

    def get_context_data(self, **kwargs):
        context = super(CommentListView, self).get_context_data(**kwargs)
        context['form'] = CommentSearchForm(self.request.GET)
        context['tag_form'] = CommentTagForm(self.request.GET)
        return context

    def get_queryset(self):
        qs = super(CommentListView, self).get_queryset()
        get = self.request.GET
        if 'comment' in get and get['comment'] != '':
            qs = qs.filter(comment__icontains=get['comment'])
        if 'user_name' in get and get['user_name'] != '':
            qs = qs.filter(user_name__icontains=get['user_name'])
        if 'tag' in get and get['tag'] != '':
            tags = Tag.objects.filter(name=get['tag'])
            tagged = TaggedItem.objects.get_intersection_by_model(Comment, tags)
            qs = qs.filter(id__in=tagged)

        qs = qs.filter(is_removed=False)

        qs = qs.prefetch_related('content_object', 'content_object__dataset', 'user')
        # Filter in only objects in the datasets the user has permissions to.
        allowed_datasets = get_objects_for_user(self.request.user, 'dictionary.view_dataset')
        qs = qs.filter(id__in=[x.id for x in qs if hasattr(x.content_object, 'dataset') and x.content_object.dataset in allowed_datasets])

        return qs.order_by('-submit_date')


class CommentSearchForm(forms.Form):
    comment = forms.CharField(label=_lazy('Comment'), required=False)
    user_name = forms.CharField(label=_lazy('Username'), required=False)


class CommentRemoveTagForm(forms.Form):
    comment_id = forms.IntegerField(required=True, widget=forms.HiddenInput())
    remove_tag_id = forms.IntegerField(required=False, widget=forms.HiddenInput())


def remove_tag(request):
    if request.method == 'POST':
        form = CommentRemoveTagForm(request.POST)
        if form.is_valid():
            # Make sure that only the commenter can delete a tag.
            comment = get_object_or_404(Comment, id=form.cleaned_data["comment_id"])
            if not request.user == comment.user or not request.user.is_staff:
                return HttpResponseForbidden(_("You are not allowed to edit tags of this comment, "
                                               "because you are not the author of the comment."))
            if form.cleaned_data["remove_tag_id"]:
                tagged = get_object_or_404(TaggedItem, tag__id=form.cleaned_data["remove_tag_id"], object_id=comment.id)
                tagged.delete()
    if 'HTTP_REFERER' in request.META:
        return redirect(request.META['HTTP_REFERER'])
    else:
        return redirect(request.path)


@receiver(comment_was_posted, sender=Comment)
def add_tags_to_comments(sender, request, comment, **kwargs):
    """Add tags to a comment after comment has been created."""
    if request.method == 'POST':
        form = CommentTagForm(request.POST)
        if form.is_valid():
            if form.cleaned_data["tag"]:
                Tag.objects.add_tag(comment, form.cleaned_data["tag"].name)


class CommentTagInlineForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(CommentTagInlineForm, self).__init__(*args, **kwargs)
        ct = ContentType.objects.get_for_model(Comment)
        try:
            # Limit choices, try to get allowed tags based on ContentType from AllowedTags.
            self.fields['tag'].queryset = AllowedTags.objects.get(content_type=ct).allowed_tags.all()
        except (AttributeError, ObjectDoesNotExist):
            # Get all tags.
            self.fields['tag'].queryset = Tag.objects.all()


class CommentTagInline(TagAdminInline):
    form = CommentTagInlineForm


# Adding Tags as inline to CommentsAdmin
CommentsAdmin.inlines = [CommentTagInline, ]
CommentsAdmin.list_filter += (TagListFilter, )


def get_users_from_comment(comment):
    """Returns a QuerySet of Users mentioned in a comment with '@username'"""
    matched_usernames = re.findall(r"@\w+", comment)
    usernames_no_duplicates = set(matched_usernames)
    return User.objects.filter(username__in=[x[1:] for x in usernames_no_duplicates])


def shorten_comment(comment):
    if len(comment) > 199:
        return comment[:200]+" ..."
    return comment

@receiver(comment_was_posted, sender=Comment)
def notify_on_mention(sender, comment, request, **kwargs):
    """Add a Notification for users mentioned in a comment."""
    for user in get_users_from_comment(comment.comment):
        notify.send(sender=request.user, recipient=user, verb=_("mentioned you in a comment"), action_object=comment,
                    description=shorten_comment(comment.comment), target=comment, public=True)