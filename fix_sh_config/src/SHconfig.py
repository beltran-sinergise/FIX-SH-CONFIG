"""SentinelHub configuration management via API."""

import logging
from typing import Any

import requests
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session
from sentinelhub.config import SHConfig
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

CONFIG_URL = "https://sh.dataspace.copernicus.eu/api/v2/configuration/instances"

logger = logging.getLogger(__name__)


class ConfigBuilder:
    """Builder class for managing SentinelHub configurations via API.

    This class provides methods to list, get, update, and clone SentinelHub
    configuration instances through the CDSE API.
    """

    def __init__(self, config: SHConfig, user_id: str, domain_account_id: str):
        """Initialize ConfigBuilder with authentication and configuration details.

        Args:
            config: SentinelHub configuration object with credentials.
            user_id: User ID for API requests.
            domain_account_id: Domain account ID for API requests.
        """
        self.SHConfig = config
        self.config_url = CONFIG_URL
        self.token = self.__get_oauth_token(config)
        self.user_id = user_id
        self.domain_account_id = domain_account_id

    def __get_oauth_token(self, config: SHConfig) -> str:
        """Get an OAuth token for CDSE.

        Args:
            config (SHConfig): SHConfig object

        Returns:
            str: the Oauth token to be used in the request headers
        """
        # Create a session
        client = BackendApplicationClient(client_id=config.sh_client_id)
        oauth = OAuth2Session(client=client)

        # Get token for the session
        token = oauth.fetch_token(
            token_url=config.sh_token_url,
            client_secret=config.sh_client_secret,
            include_client_id=True,
        )
        return token["access_token"]

    def list_configs(self) -> list[dict[str, Any]]:
        """List all configurations for the given collection ID.

        Returns:
            Dict[str, Any]: Dictionary containing the configurations

        Raises:
            requests.RequestException: If the API request fails
        """
        url = "https://sh.dataspace.copernicus.eu/api/v2/configuration/instances"

        headers = {
            "accept": "application/json",
            "authorization": f"Bearer {self.token}",
        }

        params = {"domainAccountId": self.domain_account_id}

        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()  # Raises an HTTPError for bad responses

            return response.json()

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching configurations: {e}")
            raise

    def get_config(self, config_id: str) -> dict[str, Any]:
        """Get a specific configuration by ID.

        Args:
            config_id: Configuration ID to retrieve.

        Returns:
            Configuration data as a dictionary.

        Raises:
            requests.RequestException: If the API request fails.
        """
        url = f"https://sh.dataspace.copernicus.eu/api/v2/configuration/instances/{config_id}"

        headers = {
            "accept": "application/json",
            "authorization": f"Bearer {self.token}",
        }
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # Raises an HTTPError for bad responses

            return response.json()

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching configurations: {e}")
            raise

    def rename_collection(self, config_id: str, new_name: str) -> None:
        """Rename a configuration collection.

        Args:
            config_id: Configuration ID to rename.
            new_name: New name for the configuration.
        """
        url = f"https://sh.dataspace.copernicus.eu/api/v2/configuration/instances/{config_id}"

        headers = {
            "accept": "application/json",
            "authorization": f"Bearer {self.token}",
        }
        payload = {
            "id": config_id,
            "name": new_name,  # <-- The new name for the configuration
            "domainAccountId": self.domain_account_id,
        }

        try:
            requests.put(url, headers=headers, json=payload)
        except Exception as err:
            logger.error(f"An error occurred: {err}")

    def get_layers(self, config_id: str) -> list[dict[str, Any]]:
        """Get all layers for a given configuration ID.

        Args:
            config_id: The configuration ID.

        Returns:
            List of layer dictionaries containing layer information.

        Raises:
            requests.RequestException: If the API request fails.
        """
        url = f"https://sh.dataspace.copernicus.eu/api/v2/configuration/instances/{config_id}/layers"

        headers = {
            "accept": "application/json",
            "authorization": f"Bearer {self.token}",
        }

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # Raises an HTTPError for bad responses
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching layers: {e}")
            raise

    def set_layer(self, config_id: str, layer_id: str, layer: dict[str, Any]) -> None:
        """Update a specific layer in a configuration.

        Args:
            config_id: The configuration ID.
            layer_id: The layer ID to update.
            layer: Layer data dictionary with updated configuration.
        """
        url = f"https://sh.dataspace.copernicus.eu/api/v2/configuration/instances/{config_id}/layers/{layer_id}"

        headers = {
            "accept": "application/json",
            "authorization": f"Bearer {self.token}",
        }

        try:
            response = requests.put(url, headers=headers, json=layer)
            logger.info(f"Layer update response: {response.status_code}")
        except Exception as err:
            logger.error(f"An error occurred: {err}")

    def copy_config(
        self,
        source_instance_id: str,
        source_instance_name: str,
        target_domain_account_id: str,
    ) -> dict[str, Any]:
        """Clone a configuration to another domain account.

        Args:
            source_instance_id: ID of the configuration to clone.
            source_instance_name: Name of the source configuration.
            target_domain_account_id: Target domain account ID for the clone.

        Returns:
            Response data from the cloning operation.

        Raises:
            requests.RequestException: If the API request fails.
        """
        url = f"https://sh.dataspace.copernicus.eu/api/v2/configuration/instances/{source_instance_id}/clone"

        params = {"to_domain_account_id": target_domain_account_id}
        headers = {
            "accept": "application/json",
            "authorization": f"Bearer {self.token}",
        }

        payload = {
            "id": source_instance_id,
            "name": source_instance_name,
            "domainAccountId": self.domain_account_id,
        }

        try:
            response = requests.post(url, headers=headers, params=params, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error copying configuration: {e}")
            raise


class SHCredentials(BaseSettings):
    """Configuration for authentication and token handling.
    Values bare loaded from environment or a .env-like file (default: 'conf').
    """

    model_config = SettingsConfigDict(
        env_file="conf", env_file_encoding="utf-8", extra="allow"
    )

    sh_client_id: str = Field(
        description="SentinelHub client ID used to authenticate with CDSE.",
    )
    sh_client_secret: str = Field(
        description="SentinelHub client secret used to authenticate with CDSE.",
    )


def read_configuration(config_file: Path) -> SHConfig:
    """Read SentinelHub configuration from config file.

    Returns:
        SHConfig: Configured SentinelHub configuration object with client credentials
                 and CDSE endpoints.
    """

    sh_credentials = SHCredentials(_env_file=str(config_file))

    return SHConfig(
        sh_client_id=sh_credentials.sh_client_id,
        sh_client_secret=sh_credentials.sh_client_secret,
        sh_base_url="https://sh.dataspace.copernicus.eu",
        sh_token_url="https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token",
    )
