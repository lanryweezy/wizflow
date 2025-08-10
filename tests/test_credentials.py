import pytest
from unittest.mock import patch, MagicMock

from wizflow.core.credentials import CredentialManager, WIZFLOW_SERVICE_PREFIX


@pytest.fixture
def mock_keyring():
    """Fixture to mock the keyring library."""
    with patch('wizflow.core.credentials.keyring') as mock_keyring_lib:
        # Mock the get_keyring() check in __init__ to not raise an error
        mock_keyring_lib.get_keyring.return_value = MagicMock()
        yield mock_keyring_lib

def test_save_credential_keyring(mock_keyring):
    """Test successfully saving a credential using the keyring backend."""
    manager = CredentialManager()
    manager.keyring_available = True # Force keyring mode
    result = manager.save_credential("test_service", "test_user", "test_pass")

    expected_service_name = f"{WIZFLOW_SERVICE_PREFIX}-test_service"
    mock_keyring.set_password.assert_called_once_with(expected_service_name, "test_user", "test_pass")
    assert result is True

def test_get_credential_keyring(mock_keyring):
    """Test successfully retrieving a credential using the keyring backend."""
    expected_password = "super_secret_password"
    expected_service_name = f"{WIZFLOW_SERVICE_PREFIX}-test_service"
    mock_keyring.get_password.return_value = expected_password

    manager = CredentialManager()
    manager.keyring_available = True # Force keyring mode
    password = manager.get_credential("test_service", "test_user")

    mock_keyring.get_password.assert_called_once_with(expected_service_name, "test_user")
    assert password == expected_password

# It would be good to add tests for the file-based fallback as well.
# This requires mocking Path.home(), open(), os.chmod(), etc.

def test_init_no_keyring_fallback(caplog):
    """Test that CredentialManager falls back to file storage if keyring is missing."""
    with patch('wizflow.core.credentials.keyring.get_keyring', side_effect=MagicMock(side_effect=keyring.errors.NoKeyringError)):
        with patch('pathlib.Path.mkdir'): # Mock mkdir to avoid creating dirs
             manager = CredentialManager()
             assert manager.keyring_available is False
             assert "WARNING: No system keyring backend found" in caplog.text
