from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _

from users.mailing_list import subscribe_to_mailing_list, unsubscribe_from_mailing_list
from utils.supabase import get_supabase_client

import logging

logger = logging.getLogger(__name__)

class UserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular User with the given email and password."""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)

        first_name = extra_fields.pop('first_name', None)
        last_name = extra_fields.pop('last_name', None)
        if first_name and last_name:
            extra_fields['name'] = f'{first_name} {last_name}'
        elif first_name:
            extra_fields['name'] = first_name

        if extra_fields.get('auth_id', None) == "":
            extra_fields['auth_id'] = None 

        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)

class User(AbstractUser):
    objects = UserManager()

    class UserStatus(models.TextChoices):
        ACTIVE = "ACTIVE"
        DELETED = "DELETED"

    # TODO Remove username
    username = models.CharField(_('username'), max_length=254, null=True, blank=True)
    email = models.EmailField(_('email address'), unique=True, null=True, blank=True)
    auth_id = models.CharField(_('auth_id'), max_length=254, unique=True, null=True, blank=True)
    name = models.CharField(_("name"), max_length=150, blank=True, null=True)
    selected_causes = models.ManyToManyField('causes.Cause', through='causes.UserCause')
    status = models.CharField(choices=UserStatus.choices, max_length=10, default=UserStatus.ACTIVE)

    first_name = None
    last_name = None

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    # TODO Add validation to make sure email is no null if active

    def set_selected_causes(self, cause_ids: list[int]):
        from causes.models import UserCause
        # TODO Check transaction
        UserCause.objects.filter(user_id=self.pk).delete()
        UserCause.objects.bulk_create(
            [UserCause(cause_id=cause_id, user_id=self.pk) for cause_id in cause_ids]
        )
        print(f"Setting selected causes to: {cause_ids}")

    def subscribe_to_mailing_list(self):
        subscribe_to_mailing_list(self.email, self.name)

    def unsubscribe_from_mailing_list(self):
        unsubscribe_from_mailing_list(self.email)

    def delete(self):
        """Remove identifiying information of user and mark as deleted.

        A user record should not be fully deleted as this breaks relationships for other models such as action completion. These relations are useful for aggreate statistics. Instead when a user requests to delete their account any identifiying data should be removed.
        """
        logger.info(f"Deleting user id={self.pk}")

        if self.status == User.UserStatus.DELETED:
            raise Exception("User already deleted")

        if self.auth_id is None:
            raise Exception("Cannot delete user with no auth_id")

        logger.info(f"Deleting user from supabase auth_id={self.auth_id}")
        supabase = get_supabase_client()
        # TODO Handle errors
        response = supabase.auth.admin.delete_user(self.auth_id)
        logger.info(response)

        logger.info("Soft deleting user from user service")
        self.username = None
        self.name = None
        self.email = None
        self.auth_id = None
        self.status = User.UserStatus.DELETED
        self.save()
