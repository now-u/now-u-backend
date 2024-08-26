from django.db import models
from django.utils.translation import gettext_lazy as _

from app_links_client.models.link_data import LinkData

from users.models import User
from images.models import Image
from utils.app_links import create_app_links_client
from utils.models import TimeStampedMixin, ReleaseControlMixin
from utils.timestamp import datetimeToTimestamp

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
    news_articles = models.ManyToManyField('NewsArticle', related_name='causes', blank=True)

    def header_image_preview(self):
        return self.header_image.image_preview()

    def is_selected(self, user_id: str) -> bool:
        return UserCause.objects.filter(user_id=user_id, cause=self).exists()

    def select(self, user_id: str):
        UserCause.objects.create(user_id=user_id, cause=self)

    def generate_link(self):
        client = create_app_links_client()
        client.links_post(
            link_data=LinkData(
                title=self.title,
                description=self.description,
                image_url=self.header_image.get_url(),
                android_destination="https://play.google.com/store/apps/details?id=com.nowu.app",
                ios_destination="https://apps.apple.com/us/app/now-u/id1516126639",
                web_destination="now-u.com/causes",
            )
        )

    def __str__(self) -> str:
        return self.title


class Theme(models.Model):
    title = models.CharField(max_length=64)
    header_image = models.ForeignKey(Image, on_delete=models.CASCADE, null=True)
    campaigns = models.ManyToManyField('Campaign', related_name='themes', blank=True)

class LearningResource(ReleaseControlMixin, TimeStampedMixin, models.Model):
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

class Action(ReleaseControlMixin, TimeStampedMixin, models.Model):
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

class Campaign(ReleaseControlMixin, TimeStampedMixin, models.Model):
    title = models.CharField(max_length=100, unique=True)
    short_name = models.CharField(max_length=100)
    description = models.TextField()
    header_image = models.ForeignKey(Image, on_delete=models.CASCADE)
    of_the_month = models.BooleanField(default=False)
    suggested = models.BooleanField(default=False)

    actions = models.ManyToManyField('Action', related_name='campaigns', blank=True)
    learning_resources = models.ManyToManyField('LearningResource', related_name='campaigns', blank=True)

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

class NewsArticle(ReleaseControlMixin, TimeStampedMixin, models.Model):
    title = models.CharField(max_length=300)
    subtitle = models.CharField(max_length=300)
    source = models.CharField(max_length=300)
    link = models.URLField(max_length=500)
    header_image = models.ForeignKey(Image, on_delete=models.CASCADE)
    published_at = models.DateTimeField(help_text=_('The date when this resource was published by the source. The app will show news in published order by default.'))

    @property
    def published_at_timestamp(self) -> int:
        return datetimeToTimestamp(self.published_at)

    def is_completed(self, user_id: str) -> bool:
        return UserNewsArticle.objects.filter(user_id=user_id, news_article=self).exists()

    def complete(self, user_id: str):
        # TODO Prevent duplicate completion all over the replace!
        UserNewsArticle.objects.create(user_id=user_id, news_article=self)

    def uncomplete(self, user_id: str):
        UserAction.objects.filter(user_id=user_id, news_article=self).delete()

    def __str__(self) -> str:
        return self.title

class Organisation(ReleaseControlMixin, TimeStampedMixin, models.Model):
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

class UserAction(TimeStampedMixin, models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='completed_actions')
    action = models.ForeignKey(Action, on_delete=models.CASCADE)

class UserLearningResources(TimeStampedMixin, models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='completed_learning_resources')
    learning_resource = models.ForeignKey(LearningResource, on_delete=models.CASCADE)

class UserNewsArticle(TimeStampedMixin, models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='completed_news_articles')
    news_article = models.ForeignKey(NewsArticle, on_delete=models.CASCADE)

class UserCampaign(TimeStampedMixin, models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='completed_campaigns')
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE)

class UserCause(TimeStampedMixin, models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    cause = models.ForeignKey(Cause, on_delete=models.CASCADE)
