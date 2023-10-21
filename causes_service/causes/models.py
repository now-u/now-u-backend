from datetime import datetime
import time
import math
from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from users.models import User
from images.models import Image
from utils.models import TimeStampedMixin

class TimestampMixin(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class ReleaseControlManager(models.Manager):
    def filter_active(self, is_active_at: datetime, is_active=True):
        release_query = Q(release_at=None) | Q(release_at__lte=is_active_at)
        end_query = Q(end_at=None) | Q(end_at__gte=is_active_at)
        active_query = release_query & end_query
        if not is_active:
            active_query = ~active_query
        return self.filter(active_query)

class ReleaseControlMixin(TimeStampedMixin, models.Model):
    release_at = models.DateTimeField(help_text=_('The date from which this resource should be available in the app. If not provided the resource will not be visible'))
    end_at = models.DateTimeField(help_text=_('The date from which this resource should no longer be available in the app. If not provided the reosurce will stay visible after its released'), null=True, blank=True)

    objects = ReleaseControlManager()

    # TODO Add to qury set
    def active(self) -> bool:
        # TODO Handle TZ
        now = timezone.now()

        if now < self.release_at:
            return False

        if self.end_at is not None and now > self.end_at:
            return False

        return True

    @property
    def release_at_timestamp(self) -> int:
        return math.floor(time.mktime(self.release_at.timetuple()))

    class Meta:
        abstract = True

class Cause(models.Model):
    class Icon(models.TextChoices):
        EDUCATION = "cause_icon_education",
        ENVIRONMENT = "cause_icon_environment",
        HEALTH_WELLBEING = "cause_icon_health_wellbeing",
        SAFE_HOME_COMMUNITY = "cause_icon_safe_home_community",
        ECONOMIC_OPPORTUNITY = "cause_icon_economic_opportunity",
        EQUILITY_HUMAN_RIGHTS = "cause_icon_equality_human_rights",

    title = models.CharField(max_length=100, unique=True)
    icon = models.CharField(max_length=40, choices=Icon.choices)
    description = models.TextField()
    header_image = models.ForeignKey(Image, on_delete=models.CASCADE)

    themes = models.ManyToManyField('Theme', related_name='causes', blank=True)
    actions = models.ManyToManyField('Action', related_name='causes', blank=True)
    learning_resources = models.ManyToManyField('LearningResource', related_name='causes', blank=True)
    campaigns = models.ManyToManyField('Campaign', related_name='causes', blank=True)
    news_articles = models.ManyToManyField('NewsArticle', related_name='new_articles', blank=True)

    def header_image_preview(self):
        return self.header_image.image_preview()

    def is_selected(self, user_id: str) -> bool:
        return UserCause.objects.filter(user_id=user_id, cause=self).exists()

    def select(self, user_id: str):
        UserCause.objects.create(user_id=user_id, cause=self)

    def __str__(self) -> str:
        return self.title


class Theme(models.Model):
    title = models.CharField(max_length=64)
    header_image = models.ForeignKey(Image, on_delete=models.CASCADE)
    description = models.TextField()
    campaigns = models.ManyToManyField('Campaign', related_name='themes', blank=True)

class LearningResource(ReleaseControlMixin, TimestampMixin, models.Model):
    class Type(models.TextChoices):
        VIDEO = 'VIDEO', _('Video'),
        READING = 'READING', _('Reading')
        INFGRAPHIC = 'INFOGRAPHIC', _('Infographic'),
        LISTEN = 'LISTEN', _('Listen'),
        # TOOD Get rid of this
        OTHER = 'OTHER', _('Other')
        # REPORT = 'REPORT', _('Report'),
        # STORY = 'STORY', _('Story')

    campaigns: models.QuerySet['Campaign']

    title = models.CharField(max_length=200, unique=True)
    time = models.IntegerField()
    link = models.URLField(max_length=500)
    learning_resource_type = models.CharField(max_length=24, choices=Type.choices, )
    # TODO Make this way shorter
    source = models.CharField(max_length=300, )

    def is_completed(self, user_id: str) -> bool:
        return UserLearningResources.objects.filter(user_id=user_id, learning_resource=self).exists()

    def complete(self, user_id: str):
        # TODO Block this (and for other resources) if user_id is null
        UserLearningResources.objects.create(user_id=user_id, learning_resource=self)

        for campaign in self.campaigns.all():
            campaign.compute_is_completed(user_id)

    def __str__(self) -> str:
        return self.title

class Action(ReleaseControlMixin, TimestampMixin, models.Model):
    class Type(models.TextChoices):
        VOLUNTEER = 'VOLUNTEER', _('Volunteer'),
        DONATE = 'DONATE', _('Donate'),
        PURCHASE = 'PURCHASE', _('Purchase'),
        FUNDRASE = 'FUNDRAISE', _('Fundraise'),
        RAISE_AWARENESS = 'RAISE_AWARENESS', _('Raise awareness')
        SIGN = 'SIGN', _('Sign')
        BEHAVIOR = 'BEHAVIOR', _('Behavior change'),
        CONTACT = 'CONTACT', _('Contact'),
        PROTEST = 'PROTEST', _('Protest'),
        CONNECT = 'CONNECT', _('Connect'),
        LEARN = 'LEARN', _('Learn'),
        QUIZ = 'QUIZ', _('Quiz'),
        OTHER = 'OTHER', _('Other')

    campaigns: models.QuerySet['Campaign']

    title = models.CharField(max_length=200, unique=True)
    link = models.URLField(max_length=3000)
    action_type = models.CharField(max_length=24, choices=Type.choices, )
    what_description = models.TextField()
    why_description = models.TextField()
    time = models.IntegerField()
    of_the_month = models.BooleanField(default=False)
    suggested = models.BooleanField(default=False)

    def is_completed(self, user_id: str) -> bool:
        return UserAction.objects.filter(user_id=user_id, action=self).exists()

    def complete(self, user_id: str):
        # TODO Prevent duplicate completion all over the replace!
        UserAction.objects.create(user_id=user_id, action=self)

        for campaign in self.campaigns.all():
            campaign.compute_is_completed(user_id)

    def uncomplete(self, user_id: str):
        UserAction.objects.filter(user_id=user_id, action=self).delete()

        for campaign in self.campaigns.all():
            campaign.compute_is_completed(user_id)

    def __str__(self) -> str:
        return self.title

class Campaign(ReleaseControlMixin, TimestampMixin, models.Model):
    title = models.CharField(max_length=100, unique=True)
    short_name = models.CharField(max_length=100)
    description = models.TextField()
    header_image = models.ForeignKey(Image, on_delete=models.CASCADE)
    of_the_month = models.BooleanField(default=False)
    suggested = models.BooleanField(default=False)

    actions = models.ManyToManyField('Action', related_name='campaigns')
    learning_resources = models.ManyToManyField('LearningResource', related_name='campaigns')

    def _mark_complete(self, user_id: str, is_complete: bool):
        """
        Cache that the campaing has been completed.

        TODO Update cache on below
        This cache will be recalculated when:
            - a resource from the campaign is completed/uncompleted
            - the resources within the campaign are updated
        """
        if is_complete:
            UserCampaign.objects.create(user_id=user_id, campaign=self)
        else:
            UserCampaign.objects.filter(user_id=user_id, campaign=self).delete()

    def _compute_is_completed(self, user_id: str) -> bool:
        action_ids = self.actions.all().values_list('pk', flat=True)
        user_actions = UserAction.objects.filter(user_id=user_id, action_id__in=action_ids).values_list('action_id', flat=True)
        if (set(action_ids) != set(user_actions)):
            return False

        learning_resource_ids = self.learning_resources.all().values_list('pk', flat=True)
        user_learning_resources = UserLearningResources.objects.filter(user_id=user_id, learning_resource_id__in=learning_resource_ids).values_list('learning_resource_id', flat=True)

        if (set(learning_resource_ids) != set(user_learning_resources)):
            return False

        return True

    def compute_is_completed(self, user_id: str) -> bool:
        is_complete = self._compute_is_completed(user_id)
        self._mark_complete(user_id, is_complete)
        return is_complete

    def cached_is_complete(self, user_id: str) -> bool:
        return UserCampaign.objects.filter(user_id=user_id, campaign=self).exists() 

    def __str__(self) -> str:
        return self.title

class NewsArticle(ReleaseControlMixin, TimestampMixin, models.Model):
    title = models.CharField(max_length=300)
    subtitle = models.CharField(max_length=300)
    source = models.CharField(max_length=300)
    link = models.URLField(max_length=500)
    header_image = models.ForeignKey(Image, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return self.title

class Organisation(ReleaseControlMixin, TimestampMixin, models.Model):
    class OrganisationType(models.TextChoices):
        CHARITY = 'CHARITY', _('Charity'),
        SOCIAL_ENTERPISE = 'SOCIAL_ENTERPRISE', _('Social Enterprise'),
        UNKNOWN = 'UNKNOWN', _('Unknown - Please fix'),

    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    logo = models.ForeignKey(Image, on_delete=models.CASCADE)
    organisation_type = models.CharField(max_length=24, choices=OrganisationType.choices)
    website_link = models.URLField(null=True, blank=True)
    email_address = models.EmailField(null=True, blank=True)
    # TODO Work out a better way of storing geographic_reach - string is bad
    geographic_reach = models.CharField(max_length=100, null=True, blank=True)
    instagram_link = models.URLField(null=True, blank=True)
    facebook_link = models.URLField(null=True, blank=True)
    twitter_link = models.URLField(null=True, blank=True)

class OrganisationExtraLink(models.Model):
    organisation = models.ForeignKey(Organisation, on_delete=models.CASCADE, related_name='extra_links')
    title = models.CharField(max_length=100)
    link = models.URLField()

class UserAction(TimestampMixin, models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='completed_actions')
    action = models.ForeignKey(Action, on_delete=models.CASCADE)

class UserLearningResources(TimestampMixin, models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='completed_learning_resources')
    learning_resource = models.ForeignKey(LearningResource, on_delete=models.CASCADE)

class UserCampaign(TimestampMixin, models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='completed_campaigns')
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE)

class UserCause(TimestampMixin, models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    cause = models.ForeignKey(Cause, on_delete=models.CASCADE)
