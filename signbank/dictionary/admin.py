# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from reversion.admin import VersionAdmin
from django.utils.translation import ugettext as _
from modeltranslation.admin import TranslationAdmin as ModelTranslationAdmin
from guardian.admin import GuardedModelAdmin

from .models import Dataset, Gloss, Translation, Relation, RelationToForeignSign, Definition, GlossURL, \
    Language, SignLanguage, Dialect, FieldChoice, GlossRelation, MorphologyDefinition

from ..video.admin import GlossVideoInline


class DatasetAdmin(GuardedModelAdmin):
    model = Dataset
    list_display = ('name', 'is_public', 'signlanguage',)


class TranslationAdmin(admin.ModelAdmin):
    search_fields = ['^keyword__text', '^gloss__idgloss']
    list_filter = ('gloss__dataset',)
    list_display = ('gloss', 'keyword')


class TranslationInline(admin.TabularInline):
    model = Translation
    extra = 1
    raw_id_fields = ['keyword']


class RelationToOtherSignInline(admin.TabularInline):
    model = Relation
    extra = 1


class RelationToForeignSignInline(admin.TabularInline):
    model = RelationToForeignSign
    extra = 1
    classes = ('collapse',)


class DefinitionInline(admin.TabularInline):
    model = Definition
    extra = 1
    classes = ('collapse',)


class RelationInline(admin.TabularInline):
    model = Relation
    fk_name = 'source'
    raw_id_fields = ['source', 'target']
    # Translators: verbose_name_plural
    verbose_name_plural = _("Relations to other Glosses")
    extra = 1


class GlossURLInline(admin.TabularInline):
    model = GlossURL
    extra = 1


def publish(modeladmin, request, queryset):
    queryset.update(published=True)
publish.short_description = _("Publish selected glosses")


def unpublish(modeladmin, request, queryset):
    queryset.update(published=False)
unpublish.short_description = _("Unpublish selected glosses")


class GlossAdmin(VersionAdmin):
    # Making sure these fields are not edited in admin
    readonly_fields = ('created_at', 'created_by', 'updated_at', 'updated_by',)
    actions = [publish, unpublish]

    fieldsets = ((None, {'fields': ('dataset', 'published', 'idgloss', 'idgloss_en', 'notes',)},),
                 (_('Created/Updated'), {'fields': ('created_at', 'created_by', 'updated_at', 'updated_by')},),
                 (_('Publication Status'), {'fields': ('in_web_dictionary', 'is_proposed_new_sign',),
                                         'classes': ('collapse',)},),
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
    list_display = ['idgloss', 'dataset', 'published', 'idgloss_en']
    search_fields = ['^idgloss']
    list_filter = ('dataset', 'published',)
    inlines = [GlossVideoInline, GlossURLInline, TranslationInline, RelationInline, RelationToForeignSignInline,
               DefinitionInline, ]

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


class LanguageAdmin(VersionAdmin, ModelTranslationAdmin):
    model = Language


class SignLanguageAdmin(VersionAdmin):
    model = SignLanguage
    inlines = [DialectInline]


class FieldChoiceAdmin(admin.ModelAdmin):
    model = FieldChoice
    list_display = ('field', 'english_name', 'machine_value',)


class GlossRelationAdmin(VersionAdmin):
    raw_id_fields = ('source', 'target',)
    model = GlossRelation
    list_display = ('source', 'target',)
    list_filter = ('source__dataset',)
    search_fields = ('source',)


admin.site.register(Language, LanguageAdmin)
admin.site.register(SignLanguage, SignLanguageAdmin)
admin.site.register(Gloss, GlossAdmin)
admin.site.register(Translation, TranslationAdmin)
admin.site.register(FieldChoice, FieldChoiceAdmin)
admin.site.register(MorphologyDefinition)
admin.site.register(Dataset, DatasetAdmin)
admin.site.register(GlossRelation, GlossRelationAdmin)
