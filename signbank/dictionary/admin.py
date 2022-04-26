# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.forms import Textarea
from django.db import models
from django.contrib import admin
from django.utils.translation import ugettext as _
from django.utils.translation import ugettext_lazy as _lazy
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.admin import GenericTabularInline
from django.forms import ModelForm
from django.core.exceptions import ObjectDoesNotExist


from reversion.admin import VersionAdmin
from modeltranslation.admin import TranslationAdmin as ModelTranslationAdmin
from guardian.admin import GuardedModelAdmin

from tagging.models import TaggedItem, Tag

from .models import Dataset, Gloss, Signer, Translation, GlossURL, Language, SignLanguage, Dialect, FieldChoice, GlossRelation,\
    AllowedTags, GlossTranslations
from ..video.admin import GlossVideoInline


class TagListFilter(admin.SimpleListFilter):
    title = _('Tag')
    parameter_name = 'tag'

    def lookups(self, request, model_admin):
        tags = Tag.objects.usage_for_model(model_admin.model)
        return [(tag.name, _(tag.name)) for tag in tags]

    def queryset(self, request, queryset):
        if self.value():
            ct = ContentType.objects.get_for_model(queryset.model)
            return queryset.filter(id__in=[x.object_id for x in TaggedItem.objects.filter(tag__name=self.value(),
                                                                                          content_type=ct)])


class DatasetAdmin(GuardedModelAdmin, ModelTranslationAdmin):
    model = Dataset
    list_display = ('name', 'is_public', 'signlanguage',)


class TranslationAdmin(admin.ModelAdmin):
    search_fields = ['^keyword__text', '^gloss__idgloss']
    list_filter = ('gloss__dataset',)
    list_display = ('gloss', 'keyword')


class TranslationInline(admin.TabularInline):
    model = Translation
    extra = 0

    def get_readonly_fields(self, request, obj=None):
        # Set all fields to be read only.
        return list(set(
            [field.name for field in self.opts.local_fields] +
            [field.name for field in self.opts.local_many_to_many]
        ))

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class AllowedTagsAdmin(VersionAdmin):
    model = AllowedTags
    list_display = ('content_type',)


class TagAdminInline(GenericTabularInline):
    model = TaggedItem
    extra = 0


class GlossRelationTagAdminInlineForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(GlossRelationTagAdminInlineForm, self).__init__(*args, **kwargs)
        ct = ContentType.objects.get_for_model(GlossRelation)
        try:
            # Limit choices, try to get allowed tags based on ContentType from AllowedTags.
            self.fields['tag'].queryset = AllowedTags.objects.get(content_type=ct).allowed_tags.all()
        except (AttributeError, ObjectDoesNotExist):
            # Get all tags.
            self.fields['tag'].queryset = Tag.objects.all()


class GlossRelationTagAdminInline(TagAdminInline):
    verbose_name = _('Relation type')
    verbose_name_plural = _('Relation types')
    form = GlossRelationTagAdminInlineForm


class GlossRelationAdmin(VersionAdmin):
    raw_id_fields = ('source', 'target',)
    model = GlossRelation
    list_display = ('source', 'tag', 'target',)
    list_filter = ('source__dataset', TagListFilter)
    search_fields = ('source',)
    inlines = [GlossRelationTagAdminInline, ]


class GlossRelationInline(admin.TabularInline):
    model = GlossRelation
    raw_id_fields = ['source', 'target']
    extra = 1
    fk_name = 'source'
    verbose_name = _("Gloss relation")
    verbose_name_plural = _("Gloss relations")


class GlossURLInline(admin.TabularInline):
    model = GlossURL
    extra = 1


class GlossTagInlineForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(GlossTagInlineForm, self).__init__(*args, **kwargs)
        ct = ContentType.objects.get_for_model(Gloss)
        try:
            # Limit choices, try to get allowed tags based on ContentType from AllowedTags.
            self.fields['tag'].queryset = AllowedTags.objects.get(content_type=ct).allowed_tags.all()
        except (AttributeError, ObjectDoesNotExist):
            # Get all tags.
            self.fields['tag'].queryset = Tag.objects.all()


class GlossTagInline(TagAdminInline):
    form = GlossTagInlineForm


class GlossTranslationsInline(admin.TabularInline):
    model = GlossTranslations
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows':5, 'cols':50})},
    }
    fields = ('language', 'translations', 'translations_secondary', 'translations_minor')
    extra = 0

    def has_add_permission(self, request):
        #return False
        return True

    def has_delete_permission(self, request, obj=None):
        return False


def publish(modeladmin, request, queryset):
    queryset.update(published=True)


def unpublish(modeladmin, request, queryset):
    queryset.update(published=False)


publish.short_description = _("Publish selected glosses")
unpublish.short_description = _("Unpublish selected glosses")


def exclude_from_ecv(modeladmin, request, queryset):
    queryset.update(exclude_from_ecv=True)


def include_in_ecv(modeladmin, request, queryset):
    queryset.update(exclude_from_ecv=False)


exclude_from_ecv.short_description = _("Exclude glosses from ECV")
include_in_ecv.short_description = _("Include glosses in ECV")


class GlossAdmin(VersionAdmin):
    # Making sure these fields are not edited in admin
    readonly_fields = ('created_at', 'created_by', 'updated_at', 'updated_by',)
    actions = [publish, unpublish, exclude_from_ecv, include_in_ecv]

    fieldsets = ((None, {'fields': ('dataset', 'published', 'exclude_from_ecv', 'idgloss', 'idgloss_mi', 'notes', 'hint', 'signer')},),
                 (_('Created/Updated'), {'fields': ('created_at', 'created_by', 'updated_at', 'updated_by')},),
                 (_('Phonology'), {'fields': ('handedness', 'location', 'strong_handshape', 'weak_handshape',
                                              'relation_between_articulators', 'absolute_orientation_palm',
                                              'absolute_orientation_fingers', 'relative_orientation_movement',
                                              'relative_orientation_location', 'orientation_change',
                                              'handshape_change', 'repeated_movement', 'alternating_movement',
                                              'movement_shape', 'movement_direction', 'movement_manner', 'contact_type',
                                              'phonology_other', 'mouth_gesture', 'mouthing', 'phonetic_variation'),
                                   'classes': ('collapse',)},),
                 (_('Semantics'), {'fields': ('iconic_image', 'named_entity', 'semantic_field'),
                                   'classes': ('collapse',)}),
                 (_('Frequency'), {'fields': ('number_of_occurences',), 'classes': ('collapse',)}),
                 )
    save_on_top = True
    save_as = True
    list_display = ['idgloss', 'dataset', 'published', 'exclude_from_ecv', 'idgloss_mi']
    search_fields = ['^idgloss']
    list_filter = ('dataset', 'published', 'exclude_from_ecv', TagListFilter, )
    inlines = [GlossVideoInline, GlossTranslationsInline, TranslationInline, GlossRelationInline, GlossURLInline, GlossTagInline, ]

    def get_readonly_fields(self, request, obj=None):
        """
        Adds 'published' to 'readonly_fields' if user does not have permission to publish glosses.
        """
        # If obj is not None (and exists), return only the variable 'readonly_fields'
        if obj is None:
            return self.readonly_fields

        # If user doesn't have permission 'dictionary.lock_gloss' add it to readonly_fields
        if not request.user.has_perm('dictionary.publish_gloss'):
            self.readonly_fields += ('publish',)
        return self.readonly_fields

    def save_model(self, request, obj, form, change):
        """Sets created_by and updated_by as the original requests user"""
        obj.created_by = request.user
        obj.updated_by = request.user
        obj.save()

    def save_formset(self, request, form, formset, change):
        """Saves the formsets created_by and updated_by with request.user"""
        if formset.model == Gloss:
            instances = formset.save(commit=False)
            for instance in instances:
                instance.created_by = request.user
                instance.updated_by = request.user
                instance.save()
        else:
            formset.save()


class DialectInline(admin.TabularInline):
    model = Dialect
    extra = 0


class LanguageAdmin(VersionAdmin, ModelTranslationAdmin):
    model = Language


class SignLanguageAdmin(VersionAdmin, ModelTranslationAdmin):
    model = SignLanguage
    inlines = [DialectInline]


class FieldChoiceAdmin(admin.ModelAdmin):
    model = FieldChoice
    list_display = ('field', 'english_name', 'machine_value',)

class SignerAdmin(VersionAdmin):
    model = Signer
    list_display = ('name',)

admin.site.register(Language, LanguageAdmin)
admin.site.register(SignLanguage, SignLanguageAdmin)
admin.site.register(Gloss, GlossAdmin)
admin.site.register(Translation, TranslationAdmin)
admin.site.register(Dataset, DatasetAdmin)
admin.site.register(GlossRelation, GlossRelationAdmin)
admin.site.register(AllowedTags, AllowedTagsAdmin)
admin.site.register(Signer, SignerAdmin)

# The following models have been removed from the admin because they are not used at the moment.
# admin.site.register(FieldChoice, FieldChoiceAdmin)
# admin.site.register(MorphologyDefinition)
