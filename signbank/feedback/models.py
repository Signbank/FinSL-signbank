from django.contrib.auth import models as authmodels
from django.utils.translation import ugettext as _

from signbank.dictionary.models import *
import string
# from signbank.dictionary.models import Gloss

# models to represent the feedback from users in the site

# Translators:
isAuslanChoices = ((1, _("yes")),
                   # Translators:
                   (2, _("Perhaps")),
                   # Translators:
                   (3, _("Don't know")),
                   # Translators:
                   (4, _("Don't think so")),
                   # Translators:
                   (5, _("No")),
                   # Translators:
                   (0, _("N/A"))
                   )

# TODO: Implement Finnish choices here!
if settings.LANGUAGE_NAME == "BSL":
    whereusedChoices = (('Belfast', 'Belfast'),
                        ('Birmingham', 'Birmingham'),
                        ('Bristol', 'Bristol'),
                        ('Cardiff', 'Cardiff'),
                        ('Glasgow', 'Glasgow'),
                        ('London', 'London'),
                        ('Manchester', 'Manchester'),
                        ('Newcastle', 'Newcastle'),
                        ('Other', 'Other (note in comments)'),
                        ("Don't Know", "Don't Know"),
                        ('N/A', 'N/A'),
                        )
else:
    whereusedChoices = (('auswide', 'Australia Wide'),
                        ('dialectN', 'Dialect Sign (North)'),
                        ('dialectS', 'Dialect Sign (South)'),
                        ('nsw', "New South Wales"),
                        ('vic', "Victoria"),
                        ('qld', "Queensland"),
                        ('wa', "Western Australia"),
                        ('sa', "South Australia"),
                        ('tas', "Tasmania"),
                        ('nt', "Northern Territory"),
                        ('act', "Australian Capital Territory"),
                        ('dk', "Don't Know"),
                        ('n/a', "N/A")
                        )
# Translators: Choices (feedback)
likedChoices = ((1, _("yes")),
                # Translators:
                (2, _("A little")),
                # Translators:
                (3, _("Don't care")),
                # Translators:
                (4, _("Not much")),
                # Translators:
                (5, _("No")),
                # Translators:
                (0, _("N/A"))
                )
# Translators: Choices (feedback)
useChoices = ((1, _("yes")),
              # Translators:
              (2, _("Sometimes")),
              # Translators:
              (3, _("Not Often")),
              # Translators:
              (4, _("No")),
              # Translators:
              (0, _("N/A"))
              )
# Translators: Choices (feedback)
suggestedChoices = ((1, _("yes")),
                    # Translators: Choice
                    (2, _("Sometimes")),
                    # Translators:
                    (3, _("Don't Know")),
                    # Translators:
                    (4, _("Perhaps")),
                    # Translators:
                    (5, _("No")),
                    # Translators:
                    (0, _("N/A"))
                    )
# Translators: Choices (feedback)
correctChoices = ((1, _("yes")),
                  # Translators:
                  (2, _("Mostly Correct")),
                  # Translators:
                  (3, _("Don't Know")),
                  # Translators:
                  (4, _("Mostly Wrong")),
                  # Translators:
                  (5, _("No")),
                  # Translators:
                  (0, _("N/A"))
                  )

handformChoices = (
    # Translators: Handform choice (feedback)
    (1, _('One handed')),
    # Translators: Handform choice (feedback)
    (2, _('Two handed (same shape for each hand)')),
    # Translators: Handform choice (feedback)
    (3, _('Two handed (diffent shapes for each hand)'))
)
# Translators: handshapeChoices
handshapeChoices = ((0, _('None')),
                    # Translators: handShapeChoices
                    (291, _('Animal')),
                    (292, _('Animal-flick')),
                    (293, _('Bad')),
                    (294, _('Ball')),
                    (295, _('Cup')),
                    (296, _('Cup-flush')),
                    (297, _('Cup-thumb')),
                    (298, _('Eight')),
                    (299, _('Eight-hook')),
                    (300, _('Fist-A')),
                    (301, _('Fist-S')),
                    (302, _('Flat')),
                    (303, _('Flat-bent')),
                    (304, _('Flat-B')),
                    (305, _('Flat-flush')),
                    (306, _('Flick')),
                    (307, _('Flick-gay')),
                    (308, _('Four')),
                    (309, _('Five')),
                    (310, _('Good')),
                    (311, _('Good-6')),
                    (312, _('Gun')),
                    (313, _('Gun-hook')),
                    (314, _('Hook')),
                    (315, _('Kneel')),
                    (316, _('Letter-C')),
                    (317, _('Letter-M')),
                    (318, _('Letter-N')),
                    (319, _('Love')),
                    (320, _('Middle')),
                    (321, _('Mother')),
                    (322, _('Nine')),
                    (323, _('Point-1')),
                    (324, _('Point-D')),
                    (325, _('Point-flush')),
                    (326, _('Okay-flat')),
                    (327, _('Okay-F')),
                    (328, _('Okay-O')),
                    (329, _('Old-seven')),
                    (330, _('Plane')),
                    (331, _('Perth')),
                    (332, _('Round-O')),
                    (333, _('Round-flat')),
                    (334, _('Round-E')),
                    (335, _('Rude')),
                    (336, _('Salt')),
                    (337, _('Salt-flick')),
                    (338, _('Small')),
                    (339, _('Soon')),
                    (340, _('Spoon')),
                    (341, _('Spoon-hook')),
                    (342, _('Spoon-thumb')),
                    (343, _('Thick')),
                    (344, _('Three')),
                    (345, _('Three-hook')),
                    (346, _('Two')),
                    (347, _('Wish')),
                    (348, _('Write')),
                    (349, _('Write-flat'))
                    )
# Translators: locationChoices
locationChoices = ((0, _('None')),
                   (257, _('Top of head')),
                   (258, _('Forehead')),
                   (259, _('Temple')),
                   (260, _('Eyes')),
                   (261, _('Nose')),
                   (262, _('Whole of face')),
                   (263, _('Cheekbone')),
                   (264, _('Ear')),
                   (265, _('Cheek')),
                   (266, _('Mouth and lips')),
                   (267, _('Chin')),
                   (268, _('Neck')),
                   (269, _('Shoulder')),
                   (270, _('Chest')),
                   (271, _('Stomach')),
                   (272, _('Waist')),
                   (273, _('Lower waist')),
                   (274, _('Upper arm')),
                   (275, _('Elbow'))
                   )
# Translators: handbodycontactChoices
handbodycontactChoices = ((0, _('None')),
                          (240, _('Contact at start of movement')),
                          (241, _('Contact at end of movement')),
                          (242, _('Two contacts (tap)')),
                          (243, _('Contact during (rub/stroke)'))
                          )
# Translators: directionChoices
directionChoices = ((0, _('None')),
                    (472, _('Up')),
                    (473, _('Down')),
                    (474, _('Up and down')),
                    (475, _('Left')),
                    (476, _('Right')),
                    (477, _('Side to side')),
                    (478, _('Away')),
                    (479, _('Towards')),
                    (480, _('To and fro'))
                    )
# Translators: movementtypeChoices
movementtypeChoices = ((0, _('None')),
                       (481, _('Straight')),
                       (482, _('Curved')),
                       (483, _('Circle')),
                       (484, _('Zig-zag'))
                       )
# Translators: smallmovementChoices
smallmovementChoices = ((0, _('None')),
                        (485, _('Straighten from bent')),
                        (486, _('Bend fingers')),
                        (487, _('Nod at wrist')),
                        (488, _('Straighten fingers')),
                        (489, _('Open handshape')),
                        (490, _('Close handshape')),
                        (491, _('Wriggle fingers')),
                        (492, _('Crumble fingers'))
                        )
# Translators: repetitionChoices
repetitionChoices = ((0, _('None')),
                     (493, _('Do the movement once')),
                     (494, _('Do the movement twice')),
                     (495, _('Repeat the movement several times'))
                     )
# Translators: relativelocationChoices
relativelocationChoices = ((0, _('None')),
                           (283, _('Forearm')),
                           (284, _('Wrist')),
                           (285, _('Pulse')),
                           (286, _('Back of hand')),
                           (287, _('Palm')),
                           (288, _('Sides of hand')),
                           (289, _('Fingertips'))
                           )
# Translators: handinteractionChoices
handinteractionChoices = ((0, _('None')),
                          (468,
                           _('Alternate hands (one moves, then the other moves)')),
                          (469, _('Move the hands towards each other')),
                          (470, _('Move the hands away from each other')),
                          (471, _('The hands cross over each other'))
                          )


def t(message):
    """Replace $country and $language in message with dat from settings"""

    tpl = string.Template(message)
    return tpl.substitute(country=settings.COUNTRY_NAME, language=settings.LANGUAGE_NAME)


STATUS_CHOICES = (('unread', 'unread'),
                  ('read', 'read'),
                  ('deleted', 'deleted'),
                  )


class InterpreterFeedback(models.Model):
    """Feedback on a sign from an interpreter"""

    class Meta:
        ordering = ['-date']
        permissions = (
            ('view_interpreterfeedback', "Can View Interpreter Feedback"),)

    gloss = models.ForeignKey(Gloss)
    comment = models.TextField('Note')
    user = models.ForeignKey(authmodels.User)
    date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default='unread')


class GeneralFeedback(models.Model):
    comment = models.TextField(blank=True)
    video = models.FileField(
        upload_to=settings.COMMENT_VIDEO_LOCATION, blank=True)
    user = models.ForeignKey(authmodels.User)
    date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default='unread')

    class Meta:
        ordering = ['-date']


class SignFeedback(models.Model):
    """Store feedback on a particular sign"""

    user = models.ForeignKey(authmodels.User, editable=False)
    date = models.DateTimeField(auto_now_add=True)

    translation = models.ForeignKey(Translation, editable=False)
    # Translators: Question (sign feedback)
    comment = models.TextField(
        _("Please give us your comments about this sign. For example: do you think there are other keywords that belong with this sign? Please write your comments or new keyword/s below."),
        blank=True)
    # Translators: Question (sign feedback)
    kwnotbelong = models.TextField(
        _("Is there a keyword or keyword/s that DO NOT belong with this sign? Please provide the list of keywords below"),
        blank=True)
    # Translators: Question (sign feedback)
    isAuslan = models.IntegerField(
        t(_("Is this sign an $language Sign?")), choices=isAuslanChoices)
    # Translators: Question (sign feedback)
    whereused = models.CharField(
        _("Where is this sign used?"), max_length=10, choices=whereusedChoices)
    # Translators: Question (sign feedback)
    like = models.IntegerField(_("Do you like this sign?"), choices=likedChoices)
    # Translators: Question (sign feedback)
    use = models.IntegerField(_("Do you use this sign?"), choices=useChoices)
    # Translators: Question (sign feedback)
    suggested = models.IntegerField(
        _("If this sign is a suggested new sign, would you use it?"), default=3, choices=suggestedChoices)
    # Translators: Question (sign feedback)
    correct = models.IntegerField(
        _("Is the information about the sign correct?"), choices=correctChoices)
    # Translators: Question (sign feedback)
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default='unread')

    def __unicode__(self):
        return unicode(self.translation.translation) + " by " + unicode(self.user) + " on " + unicode(self.date)

    class Meta:
        ordering = ['-date']


class MissingSignFeedback(models.Model):
    user = models.ForeignKey(authmodels.User)
    date = models.DateTimeField(auto_now_add=True)
    handform = models.IntegerField(
        choices=handformChoices, blank=True, default=0)
    handshape = models.IntegerField(
        choices=handshapeChoices, blank=True, default=0)
    althandshape = models.IntegerField(
        choices=handshapeChoices, blank=True, default=0)
    location = models.IntegerField(
        choices=locationChoices, blank=True, default=0)
    relativelocation = models.IntegerField(
        choices=relativelocationChoices, blank=True, default=0)
    handbodycontact = models.IntegerField(
        choices=handbodycontactChoices, blank=True, default=0)
    handinteraction = models.IntegerField(
        choices=handinteractionChoices, blank=True, default=0)
    direction = models.IntegerField(
        choices=directionChoices, blank=True, default=0)
    movementtype = models.IntegerField(
        choices=movementtypeChoices, blank=True, default=0)
    smallmovement = models.IntegerField(
        choices=smallmovementChoices, blank=True, default=0)
    repetition = models.IntegerField(
        choices=repetitionChoices, blank=True, default=0)
    meaning = models.TextField()
    comments = models.TextField(blank=True)
    video = models.FileField(
        upload_to=settings.COMMENT_VIDEO_LOCATION, blank=True)

    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default='unread')

    class Meta:
        ordering = ['-date']
