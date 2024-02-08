"""Models list for 'zoho_token' app."""

from django.db import models


class ZohoOAuth(models.Model):
    """Model for token storage table."""

    client_id = models.CharField(max_length=60, blank=True, null=True, verbose_name="Client id")
    client_secret = models.CharField(
        max_length=250, blank=True, null=True, verbose_name="Client secret"
    )
    grant_token = models.CharField(
        max_length=250, blank=True, null=True, verbose_name="Grant token"
    )
    refresh_token = models.CharField(
        max_length=250, blank=True, null=True, verbose_name="Refresh token"
    )
    redirect_url = models.CharField(
        max_length=250, blank=True, null=True, verbose_name="Redirect url"
    )
    access_token = models.CharField(
        max_length=250, blank=True, null=True, verbose_name="Access token"
    )
    token_id = models.CharField(max_length=100, blank=True, null=True, verbose_name="Token id")
    expires_in = models.BigIntegerField(verbose_name="Time expire")
    user_email = models.EmailField(verbose_name="User email")

    def __str__(self):
        """Represent instances of the class in docs, admins, etc."""
        return self.user_email

    class Meta:
        verbose_name = "Zoho OAuth token"
