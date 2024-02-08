"""Models for 'custom_auth' app."""
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin, UserManager
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.mail import send_mail
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from custom_auth.validators import phone_number_validator


class CustomAbstractUser(AbstractBaseUser, PermissionsMixin):
    """
    An abstract base class implementing a fully featured User model.

    With admin-compliant permissions.

    Username, phone_number and password are required. Other fields are optional.
    """

    username_validator = UnicodeUsernameValidator()

    username = models.CharField(
        _("username"),
        max_length=150,
        help_text=_("Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only."),
        validators=[username_validator],
        error_messages={
            "unique": _("A user with that username already exists."),
        },
    )
    phone_number = models.CharField(
        max_length=30,
        unique=True,
        help_text=_("Required. 30 characters or fewer. Digits and /+/ / only."),
        validators=[phone_number_validator],
        error_messages={
            "unique": _("A user with that phone number already exists."),
        },
        verbose_name="Phone number",
    )  # TODO add validation, alter field length
    email = models.EmailField(_("email address"), blank=True)
    zoho_id = models.BigIntegerField(blank=True, null=True, verbose_name="Zoho id")
    is_staff = models.BooleanField(
        _("staff status"),
        default=False,
        help_text=_("Designates whether the user can log into this admin site."),
    )
    is_active = models.BooleanField(
        _("active"),
        default=True,
        help_text=_(
            "Designates whether this user should be treated as active. "
            "Unselect this instead of deleting accounts."
        ),
    )
    date_joined = models.DateTimeField(_("date joined"), default=timezone.now)

    objects = UserManager()

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "phone_number"
    REQUIRED_FIELDS = ["username"]

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")
        abstract = True

    def clean(self) -> None:
        """Normalize email data before saving."""
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        send_mail(subject, message, from_email, [self.email], **kwargs)

    def __str__(self) -> str:
        """To represent class instance."""
        return str(self.username)


class User(CustomAbstractUser):
    """
    Users within the Django authentication system are represented by this model.

    Username and password are required. Other fields are optional.
    """

    class Meta(CustomAbstractUser.Meta):
        swappable = "AUTH_USER_MODEL"
