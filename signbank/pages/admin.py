from django import forms
from django.contrib import admin
from signbank.pages.models import Page, PageVideo
from signbank.video.fields import VideoUploadToFLVField
from django.utils.translation import ugettext_lazy as _

from django_summernote.admin import SummernoteModelAdmin

from modeltranslation.admin import TranslationAdmin


from signbank.log import debug


class PageForm(forms.ModelForm):
    url = forms.RegexField(
        # Translators: Label for PageForm
        label=_("URL"), max_length=100, regex=r'^[-\w/]+$',
        # Translators: Help_text for PageForm
        help_text=_("Example: '/about/contact/'. Make sure to have leading"
                                       " and trailing slashes."),
        # Translators: error_message for PageForm
        error_message=_("This value must contain only letters, numbers,"
                                           " underscores, dashes or slashes."))

    class Meta:
        model = Page
        fields = "__all__"


class PageVideoForm(forms.ModelForm):
    # Translators: PageVideoForm label
    video = VideoUploadToFLVField(label=_('Video'),
                                  required=True,
                                  prefix='pages',
                                  # Translators: help_text for PageVideoForm
                                  help_text=_(
                                      "Uploaded video will be converted to Flash"),
                                  widget=admin.widgets.AdminFileWidget)

    class Meta:
        model = PageVideo
        fields = "__all__"

    def save(self, commit=True):
        debug("Saving a video form")
        debug("VideoName: %s" % (self.cleaned_data['video'],))
        debug("Cleaned data: %s" % (self.cleaned_data,))
        instance = super(PageVideoForm, self).save(commit=commit)
        debug("Instance video: %s" % instance.video)
        return instance


class PageVideoInline(admin.TabularInline):
    form = PageVideoForm
    model = PageVideo
    extra = 1

# Adds SummernoteModelAdmin and TranslationAdmin (Modeltranslation), the settings are for Summernote
class PageAdmin(SummernoteModelAdmin, TranslationAdmin):
    form = PageForm
    fieldsets = (
        (None, {
         'fields': ('url', 'title', 'parent', 'index', 'publish', 'content')}),
        (_('Advanced options'), {
         'classes': ('collapse',), 'fields': ('group_required', 'template_name')}),
    )
    list_display = ('url', 'title', 'parent', 'index')
    list_filter = ('publish', 'group_required')
    search_fields = ('url', 'title')
    inlines = [PageVideoInline]


admin.site.register(Page, PageAdmin)
