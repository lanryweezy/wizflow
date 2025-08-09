"""
Secure Credential Management for WizFlow using the system's keyring
with a fallback to an insecure JSON file.
"""

import keyring
from keyring.errors import PasswordDeleteError, NoKeyringError
from typing import Optional, Dict
from pathlib import Path
import json
import os

from ..logger import get_logger

WIZFLOW_SERVICE_PREFIX = "wizflow"


class CredentialManager:
    """
    Manages storing and retrieving user credentials.
    Tries to use the system's keyring for secure storage. If no keyring
    backend is found, it falls back to an insecure JSON file and warns the user.
    """

    def __init__(self):
        self.logger = get_logger(__name__)
        self.keyring_available = False
        self.credentials_path = Path.home() / ".wizflow" / "credentials.json"

        try:
            keyring.get_keyring()
            self.keyring_available = True
            self.logger.debug("✅ System keyring backend found. Using secure credential storage.")
        except NoKeyringError:
            self.logger.warning("⚠️  **********************************************************")
            self.logger.warning("⚠️  WARNING: No system keyring backend found.")
            self.logger.warning("⚠️  Credentials will be stored in an INSECURE plaintext file:")
            self.logger.warning(f"⚠️  {self.credentials_path}")
            self.logger.warning("⚠️  It is highly recommended to install a keyring backend.")
            self.logger.warning("⚠️  e.g., `pip install keyrings.cryptfile` or `secretstorage`")
            self.logger.warning("⚠️  **********************************************************")
            self._ensure_config_dir()

    def _ensure_config_dir(self):
        """Ensure the configuration directory exists for file-based fallback."""
        self.credentials_path.parent.mkdir(parents=True, exist_ok=True)

    def _get_service_name(self, service: str) -> str:
        """Constructs the full service name with a prefix for keyring."""
        return f"{WIZFLOW_SERVICE_PREFIX}-{service}"

    def save_credential(self, service: str, username: str, password: str) -> bool:
        """Saves a credential, using keyring if available, otherwise a JSON file."""
        if self.keyring_available:
            service_name = self._get_service_name(service)
            try:
                keyring.set_password(service_name, username, password)
                self.logger.info(f"✅ Credential for '{service}' saved successfully to system keyring.")
                return True
            except Exception as e:
                self.logger.error(f"❌ Failed to save credential for '{service}' to keyring: {e}")
                return False
        else:
            return self._save_credential_to_file(service, username, password)

    def get_credential(self, service: str, username: str) -> Optional[str]:
        """Gets a credential, using keyring if available, otherwise a JSON file."""
        if self.keyring_available:
            service_name = self._get_service_name(service)
            try:
                return keyring.get_password(service_name, username)
            except Exception as e:
                self.logger.error(f"❌ Failed to retrieve credential for '{service}' from keyring: {e}")
                return None
        else:
            return self._get_credential_from_file(service, username)

    def delete_credential(self, service: str, username: str) -> bool:
        """Deletes a credential, using keyring if available, otherwise a JSON file."""
        if self.keyring_available:
            service_name = self._get_service_name(service)
            try:
                keyring.delete_password(service_name, username)
                self.logger.info(f"✅ Credential for '{service}' deleted successfully from system keyring.")
                return True
            except PasswordDeleteError:
                self.logger.warning(f"🤷 No credential found for '{service}' to delete from keyring.")
                return False
            except Exception as e:
                self.logger.error(f"❌ Failed to delete credential for '{service}' from keyring: {e}")
                return False
        else:
            return self._delete_credential_from_file(service, username)

    # --- File-based fallback methods ---

    def _load_file_credentials(self) -> Dict:
        """Loads all credentials from the JSON file."""
        if not self.credentials_path.exists():
            return {}
        with open(self.credentials_path, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}

    def _save_file_credentials(self, creds: Dict) -> bool:
        """Saves all credentials to the JSON file with secure permissions."""
        try:
            with open(self.credentials_path, 'w') as f:
                json.dump(creds, f, indent=2)
            os.chmod(self.credentials_path, 0o600)
            return True
        except Exception as e:
            self.logger.error(f"❌ Failed to write to credential file '{self.credentials_path}': {e}")
            return False

    def _save_credential_to_file(self, service: str, username: str, password: str) -> bool:
        creds = self._load_file_credentials()
        if service not in creds:
            creds[service] = {}
        creds[service][username] = password
        success = self._save_file_credentials(creds)
        if success:
            self.logger.info(f"✅ Credential for '{service}' saved to insecure file.")
        return success

    def _get_credential_from_file(self, service: str, username: str) -> Optional[str]:
        creds = self._load_file_credentials()
        return creds.get(service, {}).get(username)

    def _delete_credential_from_file(self, service: str, username: str) -> bool:
        creds = self._load_file_credentials()
        if creds.get(service, {}).get(username):
            del creds[service][username]
            if not creds[service]:
                del creds[service]
            success = self._save_file_credentials(creds)
            if success:
                self.logger.info(f"✅ Credential for '{service}' deleted from insecure file.")
            return success
        else:
            self.logger.warning(f"🤷 No credential found for '{service}' to delete from file.")
            return False

    def load_credentials(self) -> dict:
        """
        DEPRECATED: This method is no longer supported and will be removed.
        It is only maintained for minimal backward compatibility during transition.
        """
        self.logger.warning("DEPRECATION WARNING: load_credentials() is deprecated and will be removed.")
        if self.keyring_available:
            return {}
        else:
            # In file mode, we can actually return all creds, but this is still deprecated.
            return self._load_file_credentials()
