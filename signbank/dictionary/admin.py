from django.contrib import admin
from reversion.admin import VersionAdmin

from signbank.dictionary.models import *


class KeywordAdmin(VersionAdmin):
    search_fields = ['^text']


class TranslationInline(admin.TabularInline):
    model = Translation
    extra = 1
    raw_id_fields = ['translation']


class TranslationEnglishInline(admin.TabularInline):
    model = TranslationEnglish
    extra = 1
    raw_id_fields = ['translation_english']


class RelationToOtherSignInline(admin.TabularInline):
    model = Relation
    extra = 1


class RelationToForeignSignInline(admin.TabularInline):
    model = RelationToForeignSign
    extra = 1


# raw_id_fields = ['other_lang_gloss']


class DefinitionInline(admin.TabularInline):
    model = Definition
    extra = 1


class RelationInline(admin.TabularInline):
    model = Relation
    fk_name = 'source'
    raw_id_fields = ['source', 'target']
    # Translators: verbose_name_plural
    verbose_name_plural = _("Relations to other Glosses")
    extra = 1


from django.utils.translation import ugettext_lazy as _


class GlossAdmin(VersionAdmin):
    # Making sure these fields are not edited in admin
    readonly_fields = ('created_at', 'created_by', 'updated_at', 'updated_by',)
    fieldsets = ((None, {'fields': (
        'idgloss', 'annotation_idgloss_jkl', 'annotation_idgloss_jkl_en', 'annotation_idgloss_hki',
        'annotation_idgloss_hki_en', 'annotation_comments', 'language', 'dialect', 'url_field')},),
                 ('Publication Status', {'fields': ('in_web_dictionary', 'is_proposed_new_sign',),
                                         'classes': ('collapse',)},),
                 ('Created/Updated', {'fields': ('created_at', 'created_by', 'updated_at', 'updated_by')}),
                 ('Phonology', {'fields': ('handedness', 'location', 'strong_handshape', 'weak_handshape',
                                           'relation_between_articulators', 'absolute_orientation_palm',
                                           'absolute_orientation_fingers', 'relative_orientation_movement',
                                           'relative_orientation_location', 'orientation_change',
                                           'handshape_change', 'repeated_movement', 'alternating_movement',
                                           'movement_shape', 'movement_direction', 'movement_manner', 'contact_type',
                                           'phonology_other', 'mouth_gesture', 'mouthing', 'phonetic_variation'),
                                'classes': ('collapse',)},),
                 (
                     'Semantics',
                     {'fields': ('iconic_image', 'named_entity', 'semantic_field'), 'classes': ('collapse',)}),
                 ('Frequency', {'fields': ('number_of_occurences',), 'classes': ('collapse',)}),
                 )
    save_on_top = True
    save_as = True
    list_display = ['idgloss', 'annotation_idgloss_jkl', 'annotation_idgloss_jkl_en', 'annotation_idgloss_hki',
                    'annotation_idgloss_hki_en']
    search_fields = ['^idgloss', '^annotation_idgloss_jkl']
    list_filter = [
        'language', 'dialect', 'in_web_dictionary', 'strong_handshape']
    inlines = [RelationInline, RelationToForeignSignInline,
               DefinitionInline, TranslationInline, TranslationEnglishInline]


class RegistrationProfileAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'activation_key_expired',)
    search_fields = ('user__username', 'user__first_name',)


class DialectInline(admin.TabularInline):
    model = Dialect


class DialectAdmin(VersionAdmin):
    model = Dialect


class LanguageAdmin(VersionAdmin):
    model = Language
    inlines = [DialectInline]


class FieldChoiceAdmin(admin.ModelAdmin):
    model = FieldChoice
    list_display = ('field', 'english_name', 'machine_value')


admin.site.register(Dialect, DialectAdmin)
admin.site.register(Language, LanguageAdmin)
admin.site.register(Gloss, GlossAdmin)
admin.site.register(Keyword, KeywordAdmin)
# Add the same admin interface to KeywordEnglish
admin.site.register(KeywordEnglish, KeywordAdmin)
admin.site.register(FieldChoice, FieldChoiceAdmin)
admin.site.register(MorphologyDefinition)
