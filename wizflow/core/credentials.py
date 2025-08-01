"""
Secure Credential Management for WizFlow
"""

import json
import os
from pathlib import Path
from typing import Dict, Optional


class CredentialManager:
    """
    Manages storing and retrieving user credentials securely.
    """
    def __init__(self):
        self.config_dir = Path.home() / ".wizflow"
        self.credentials_path = self.config_dir / "credentials.json"
        self._ensure_directory()

    def _ensure_directory(self):
        """Ensure the configuration directory exists."""
        self.config_dir.mkdir(parents=True, exist_ok=True)

    def load_credentials(self) -> Dict[str, str]:
        """
        Loads credentials from the JSON file.

        Returns:
            A dictionary of credentials.
        """
        if not self.credentials_path.exists():
            return {}

        # Check permissions before loading
        if self.credentials_path.stat().st_mode & 0o077:
            print(f"⚠️  Warning: Credentials file {self.credentials_path} has insecure permissions. "
                  "It should only be readable by the current user. "
                  "Please run `chmod 600 {self.credentials_path}`.")

        with open(self.credentials_path, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                print(f"⚠️  Warning: Could not parse credentials file at {self.credentials_path}. "
                      "Starting with empty credentials.")
                return {}

    def save_credentials(self, credentials: Dict[str, str]):
        """
        Saves credentials to the JSON file with secure permissions.

        Args:
            credentials: A dictionary of credentials to save.
        """
        with open(self.credentials_path, 'w') as f:
            json.dump(credentials, f, indent=2)

        # Set file permissions to be readable/writable only by the user
        os.chmod(self.credentials_path, 0o600)
        print(f"🔒 Credentials saved to {self.credentials_path}")

    def get_credential(self, key: str) -> Optional[str]:
        """
        Retrieves a single credential by key.

        Args:
            key: The key of the credential to retrieve.

        Returns:
            The credential value, or None if not found.
        """
        credentials = self.load_credentials()
        return credentials.get(key)

    def set_credential(self, key: str, value: str):
        """
        Sets a single credential and saves the file.

        Args:
            key: The key of the credential to set.
            value: The value of the credential.
        """
        credentials = self.load_credentials()
        credentials[key] = value
        self.save_credentials(credentials)
