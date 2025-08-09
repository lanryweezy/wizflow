"""
Secure Credential Management for WizFlow using the system's keyring.
"""

import keyring
from keyring.errors import PasswordDeleteError, NoKeyringError
from typing import Optional

from ..logger import get_logger

WIZFLOW_SERVICE_PREFIX = "wizflow"


class CredentialManager:
    """
    Manages storing and retrieving user credentials securely using the system's keyring.
    """

    def __init__(self):
        self.logger = get_logger(__name__)
        try:
            # Check if a keyring backend is available
            keyring.get_keyring()
        except NoKeyringError:
            self.logger.error("FATAL: No keyring backend found! Cannot store credentials securely.")
            self.logger.error("Please install a backend like 'keyrings.cryptfile' (`pip install keyrings.cryptfile`) or 'secretstorage'.")
            raise

    def _get_service_name(self, service: str) -> str:
        """Constructs the full service name with a prefix for keyring."""
        return f"{WIZFLOW_SERVICE_PREFIX}-{service}"

    def save_credential(self, service: str, username: str, password: str) -> bool:
        """
        Saves a credential to the system's keyring.

        Args:
            service: The name of the service (e.g., 'openai').
            username: The username or key name associated with the service (e.g., 'api_key').
            password: The secret to store.

        Returns:
            True if successful, False otherwise.
        """
        service_name = self._get_service_name(service)
        try:
            keyring.set_password(service_name, username, password)
            self.logger.info(f"✅ Credential for service '{service}' and username '{username}' saved successfully.")
            return True
        except Exception as e:
            self.logger.error(f"❌ Failed to save credential for '{service}': {e}")
            return False

    def get_credential(self, service: str, username: str) -> Optional[str]:
        """
        Retrieves a credential from the system's keyring.

        Args:
            service: The name of the service.
            username: The username or key name.

        Returns:
            The credential, or None if not found.
        """
        service_name = self._get_service_name(service)
        try:
            return keyring.get_password(service_name, username)
        except Exception as e:
            self.logger.error(f"❌ Failed to retrieve credential for '{service}': {e}")
            return None

    def delete_credential(self, service: str, username:str) -> bool:
        """
        Deletes a credential from the system's keyring.

        Args:
            service: The name of the service.
            username: The username or key name.

        Returns:
            True if successful, False otherwise.
        """
        service_name = self._get_service_name(service)
        try:
            keyring.delete_password(service_name, username)
            self.logger.info(f"✅ Credential for service '{service}' and username '{username}' deleted successfully.")
            return True
        except PasswordDeleteError:
            self.logger.warning(f"🤷 No credential found for service '{service}' and username '{username}' to delete.")
            return False
        except Exception as e:
            self.logger.error(f"❌ Failed to delete credential for '{service}': {e}")
            return False

    def load_credentials(self) -> dict:
        """
        DEPRECATED: This method is no longer supported with the keyring implementation
        as we cannot list all stored credentials.
        Workflows should fetch credentials individually as needed.

        Returns an empty dictionary for backward compatibility.
        """
        self.logger.warning("DEPRECATION WARNING: load_credentials() is deprecated and will be removed.")
        return {}
