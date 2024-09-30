import re
from admin.models import MarkdownField
from images.models import Image
from users.models import User
from utils.models import ReleaseControlMixin
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

slug_expr = re.compile(r'^[-\w]+$')

class Blog(ReleaseControlMixin, models.Model):
    title = models.CharField(max_length=128, unique=True)
    subtitle = models.TextField()
    slug = models.CharField(max_length= 128, unique=True, help_text=_('The text shown in the url'))
    header_image = models.ForeignKey(Image, on_delete=models.DO_NOTHING)
    reading_time = models.IntegerField()
    body = MarkdownField()
    authors = models.ManyToManyField(User, related_name='blogs', blank=True)

    def clean(self):
        if not slug_expr.match(self.slug):
            raise ValidationError({ "slug": "Slug can only contain url safe characters [a-zA-Z0-9-_]" })

    def __str__(self) -> str:
        return self.title

    class Meta:
        indexes = [
            models.Index(fields=['-release_at']),
        ]

