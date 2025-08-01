import pytest
import json
from pathlib import Path

from wizflow.core.credentials import CredentialManager

@pytest.fixture
def temp_home(tmp_path):
    """Create a temporary home directory for testing."""
    return tmp_path

@pytest.fixture
def cred_manager(monkeypatch, temp_home):
    """Fixture to create a CredentialManager instance with a mocked home directory."""
    monkeypatch.setattr(Path, 'home', lambda: temp_home)
    return CredentialManager()

def test_save_and_load_credentials(cred_manager):
    """Test saving and loading credentials."""
    creds_to_save = {"test_key": "test_value"}
    cred_manager.save_credentials(creds_to_save)

    # Check if file exists
    assert cred_manager.credentials_path.exists()

    # Check permissions (on Unix-like systems)
    import os
    if os.name != 'nt':
        assert cred_manager.credentials_path.stat().st_mode & 0o777 == 0o600

    # Check content
    loaded_creds = cred_manager.load_credentials()
    assert loaded_creds == creds_to_save

def test_set_and_get_credential(cred_manager):
    """Test setting and getting a single credential."""
    cred_manager.set_credential("my_api_key", "12345")

    retrieved_key = cred_manager.get_credential("my_api_key")
    assert retrieved_key == "12345"

    # Check another key that doesn't exist
    assert cred_manager.get_credential("non_existent_key") is None

def test_load_non_existent_credentials(cred_manager):
    """Test that loading non-existent credentials returns an empty dict."""
    assert cred_manager.load_credentials() == {}

def test_load_corrupted_credentials(cred_manager, capsys):
    """Test loading a corrupted credentials file."""
    # Create a corrupted file
    cred_manager.credentials_path.write_text("this is not json")

    loaded_creds = cred_manager.load_credentials()
    assert loaded_creds == {}

    # Check for warning message
    captured = capsys.readouterr()
    assert "Warning: Could not parse credentials file" in captured.out
