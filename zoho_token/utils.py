"""Utils class and functions for 'zoho_token' app."""

import concurrent.futures
import os
from typing import List, Optional

from dotenv import load_dotenv
from zcrmsdk.src.com.zoho.api.authenticator.oauth_token import OAuthToken
from zcrmsdk.src.com.zoho.api.authenticator.store import TokenStore
from zcrmsdk.src.com.zoho.api.logger import Logger
from zcrmsdk.src.com.zoho.crm.api.dc import EUDataCenter
from zcrmsdk.src.com.zoho.crm.api.exception import SDKException
from zcrmsdk.src.com.zoho.crm.api.initializer import Initializer
from zcrmsdk.src.com.zoho.crm.api.sdk_config import SDKConfig
from zcrmsdk.src.com.zoho.crm.api.user_signature import UserSignature

from .exceptions import SDKTokenExpired
from .models import ZohoOAuth

load_dotenv()


class ZohoOAuthHandler(TokenStore):
    """This class is to custom saving ZohoCRM OAuth2 tokens."""

    instance = None

    def get_token(self, user: UserSignature, token: OAuthToken) -> Optional[OAuthToken]:
        """
        The method to get user token details.

        Parameters:
            user (UserSignature) : A UserSignature class instance.
            token (Token) : A Token class instance.

        Returns:
            Token : A Token class instance representing the user token details.
        """
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(ZohoOAuth.objects.get, user_email=user.get_email())
            oauth_model_instance = future.result()

        if oauth_model_instance:
            oauthtoken = token
            oauthtoken.set_id(oauth_model_instance.token_id)
            oauthtoken.set_user_mail(oauth_model_instance.user_email)
            oauthtoken.set_client_id(oauth_model_instance.client_id)
            oauthtoken.set_client_secret(oauth_model_instance.client_secret)
            oauthtoken.set_refresh_token(oauth_model_instance.refresh_token)
            oauthtoken.set_access_token(oauth_model_instance.access_token)
            oauthtoken.set_grant_token(oauth_model_instance.grant_token)
            oauthtoken.set_expires_in(oauth_model_instance.expires_in)
            oauthtoken.set_redirect_url(oauth_model_instance.redirect_url)
            return oauthtoken
        raise Exception("Token does not exist")

    def save_token(self, user: UserSignature, token: OAuthToken) -> None:
        """
        The method to store user token details.

        Parameters:
            user (UserSignature) : A UserSignature class instance.
            token (Token) : A Token class instance.
        """
        token.set_user_mail(user.get_email())
        self.delete_token(token)
        defaults = {
            "client_id": token.get_client_id(),
            "client_secret": token.get_client_secret(),
            "grant_token": token.get_grant_token(),
            "refresh_token": token.get_refresh_token(),
            "redirect_url": token.get_redirect_url(),
            "access_token": token.get_access_token(),
            "token_id": token.get_id(),
            "expires_in": token.get_expires_in(),
        }
        ZohoOAuth.objects.update_or_create(user_email=user.get_email(), defaults=defaults)

    def delete_token(self, token: OAuthToken) -> None:
        """
        The method to delete user token details.

        Parameters:
            token (OAuthToken): a token class instance.
        """
        oauth_models = ZohoOAuth.objects.filter(user_email=token.get_user_mail)
        if oauth_models:
            oauth_models.delete()

    def get_tokens(self) -> List[OAuthToken]:
        """
        The method to retrieve all the stored tokens.

        Returns:
            list: a list of OAuthToken instances
        """
        oauthtokens = []
        for oauth_model_instance in ZohoOAuth.objects.all():
            oauthtoken = OAuthToken()
            oauthtoken.set_id(oauth_model_instance.token_id)
            oauthtoken.set_user_mail(oauth_model_instance.user_email)
            oauthtoken.set_client_id(oauth_model_instance.client_id)
            oauthtoken.set_client_secret(oauth_model_instance.client_secret)
            oauthtoken.set_refresh_token(oauth_model_instance.refresh_token)
            oauthtoken.set_access_token(oauth_model_instance.access_token)
            oauthtoken.set_grant_token(oauth_model_instance.grant_token)
            oauthtoken.set_expires_in(oauth_model_instance.expires_in)
            oauthtoken.set_redirect_url(oauth_model_instance.redirect_url)
            oauthtokens.append(oauthtoken)
        return oauthtokens

    def delete_tokens(self) -> None:
        """
        The method to delete all the stored tokens.
        """
        ZohoOAuth.objects.all().delete()

    def get_token_by_id(self, id: str, token: OAuthToken) -> OAuthToken:
        """
        The method to get id token details.

        Parameters:
            id (str): token id.
            token (OAuthToken): a OAuthToken class instance.

        Returns:
            OAuthToken: a OAuthToken class instance representing the id token details.
        """
        oauth_model_instance = ZohoOAuth.objects.filter(token_id=id).first()
        oauthtoken = token
        if oauth_model_instance:
            oauthtoken.set_id(oauth_model_instance.token_id)
            oauthtoken.set_user_mail(oauth_model_instance.user_email)
            oauthtoken.set_client_id(oauth_model_instance.client_id)
            oauthtoken.set_client_secret(oauth_model_instance.client_secret)
            oauthtoken.set_refresh_token(oauth_model_instance.refresh_token)
            oauthtoken.set_access_token(oauth_model_instance.access_token)
            oauthtoken.set_grant_token(oauth_model_instance.grant_token)
            oauthtoken.set_expires_in(oauth_model_instance.expires_in)
            oauthtoken.set_redirect_url(oauth_model_instance.redirect_url)
        return oauthtoken


class ZohoOAuthInitializer:
    """
    Class responsible for initializing the Zoho SDK with necessary configurations and parameters.
    Stores access and refresh tokens into DB.
    """

    instance = None

    def initialize(self, initialized: bool = False) -> None:
        """
        Initializes the Zoho SDK with the necessary configurations and parameters.
        Updates initialized access token into the DB, if parameter "refresh" is true.
        Stores initialized access and refresh toknes into the DB, if parameter "refresh" is false.

        Parameters:
            refresh (bool): Indicates whether to refresh the token during initialization. Defaults to False.
        """
        logger = Logger.get_instance(
            level=Logger.Levels.INFO, file_path=os.getenv("ZOHO_LOGGER_PATH")
        )
        user = UserSignature(email=os.getenv("ZOHO_CURRENT_USER_EMAIL"))
        environment = EUDataCenter.PRODUCTION()
        token = self._initialize_oauthtoken_instance()
        store = ZohoOAuthHandler()
        config = SDKConfig(auto_refresh_fields=True, pick_list_validation=False)
        resource_path = os.getenv("ZOHO_RESOURCE_PATH")

        Initializer.initialize(
            user=user,
            environment=environment,
            token=token,
            store=store,
            sdk_config=config,
            resource_path=resource_path,
            logger=logger,
        )
        if not initialized:
            self._obtaining_and_saving_oauth_tokens(user, store)

    def _initialize_oauthtoken_instance(self) -> OAuthToken:
        """
        Generates an OAuth token based on the provided parameters from ".env" file.

        Parameters:
            refresh (bool): Indicates whether to generate a refresh token or a grant token.

        Returns:
            OAuthToken: An instance of the OAuthToken class representing the generated token.
        """
        if ZohoOAuth.objects.exists():
            token_instance = ZohoOAuth.objects.first()
            token = OAuthToken(
                client_id=os.getenv("ZOHO_CLIENT_ID"),
                client_secret=os.getenv("ZOHO_CLIENT_SECRET"),
                grant_token=os.getenv("GRANT_TOKEN"),
                refresh_token=token_instance.refresh_token,
                access_token=token_instance.access_token,
                redirect_url=os.getenv("ZOHO_REDIRECT_URI"),
            )
        token = OAuthToken(
            client_id=os.getenv("ZOHO_CLIENT_ID"),
            client_secret=os.getenv("ZOHO_CLIENT_SECRET"),
            grant_token=os.getenv("GRANT_TOKEN"),
            redirect_url=os.getenv("ZOHO_REDIRECT_URI"),
        )
        return token

    def _obtaining_and_saving_oauth_tokens(self, user: UserSignature, store: ZohoOAuthHandler):
        """
        Stores the access token into the database.

        Parameters:
            refresh (bool): Indicates whether to refresh the token during initialization.
            user (UserSignature): An instance of the UserSignature class representing the user details.
            store (ZohoOAuthHandler): An instance of the ZohoOAuthHandler class.
        """
        try:
            Initializer.initializer.token.generate_access_token(user, store)
        except SDKException:
            raise SDKTokenExpired("Update GRANT TOKEN, because it's expired.")


zoho_init = ZohoOAuthInitializer()
