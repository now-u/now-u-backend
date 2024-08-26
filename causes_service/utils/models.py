from django.db import models
from datetime import datetime
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from utils.timestamp import datetimeToTimestamp

class ShareableMixin(models.Model):
    """Adds created_at and updated_at to a model

    Both created at and updated at are automatically set.
    """

    link_id = models.UUIDField(null=True, blank=True)
    link_url = models.URLField(null=True, blank=True)

    class Meta:
        abstract = True

class TimeStampedMixin(models.Model):
    """Adds created_at and updated_at to a model

    Both created at and updated at are automatically set.
    """

    created_at: models.DateTimeField = models.DateTimeField(auto_now_add=True)
    updated_at: models.DateTimeField = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

def filter_active_for_releaseable_queryset(
    queryset: models.QuerySet | models.Manager,
    is_active_at: datetime,
    is_active=True,
):
    release_query = Q(release_at=None) | Q(release_at__lte=is_active_at)
    end_query = Q(end_at=None) | Q(end_at__gte=is_active_at)
    active_query = release_query & end_query
    if not is_active:
        active_query = ~active_query
    return queryset.filter(active_query)

class ReleaseControlManager(models.Manager):
    def filter_active(self, is_active_at: datetime, is_active=True):
        return filter_active_for_releaseable_queryset(self, is_active_at, is_active)

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
        return datetimeToTimestamp(self.release_at)

    class Meta:
        abstract = True

