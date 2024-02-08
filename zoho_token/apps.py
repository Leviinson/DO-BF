import os
import sys

from django.apps import AppConfig
from dotenv import load_dotenv

load_dotenv()


class ZohoTokenConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "zoho_token"

    def ready(self) -> None:
        excluded_commands = ["migrate", "collectstatic", "makemigrations"]

        if any(command in sys.argv for command in excluded_commands):
            return
        from .models import ZohoOAuth
        from .utils import zoho_init

        are_oauth_tokens_exists = True if ZohoOAuth.objects.exists() else False
        is_new_grant_token_exists = False
        grant_token_from_env = os.getenv("GRANT_TOKEN")
        if are_oauth_tokens_exists:
            grant_token_from_db = ZohoOAuth.objects.first().grant_token
            if not grant_token_from_db == grant_token_from_env and grant_token_from_env:
                is_new_grant_token_exists = True

        if not are_oauth_tokens_exists or is_new_grant_token_exists and grant_token_from_env:
            zoho_init.initialize()
        if are_oauth_tokens_exists and not is_new_grant_token_exists:
            zoho_init.initialize(initialized=True)
        elif not are_oauth_tokens_exists and not grant_token_from_env:
            raise RuntimeError("Specify GRANT TOKEN in the .env file")
