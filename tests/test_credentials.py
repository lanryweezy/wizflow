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


def test_save_credential_success(mock_keyring):
    """Test successfully saving a credential."""
    manager = CredentialManager()
    result = manager.save_credential("test_service", "test_user", "test_pass")

    expected_service_name = f"{WIZFLOW_SERVICE_PREFIX}-test_service"
    mock_keyring.set_password.assert_called_once_with(expected_service_name, "test_user", "test_pass")
    assert result is True


def test_save_credential_failure(mock_keyring):
    """Test failure while saving a credential."""
    mock_keyring.set_password.side_effect = Exception("Storage error")
    manager = CredentialManager()
    result = manager.save_credential("test_service", "test_user", "test_pass")

    assert result is False


def test_get_credential_success(mock_keyring):
    """Test successfully retrieving a credential."""
    expected_password = "super_secret_password"
    expected_service_name = f"{WIZFLOW_SERVICE_PREFIX}-test_service"
    mock_keyring.get_password.return_value = expected_password

    manager = CredentialManager()
    password = manager.get_credential("test_service", "test_user")

    mock_keyring.get_password.assert_called_once_with(expected_service_name, "test_user")
    assert password == expected_password


def test_get_credential_not_found(mock_keyring):
    """Test retrieving a credential that does not exist."""
    mock_keyring.get_password.return_value = None

    manager = CredentialManager()
    password = manager.get_credential("non_existent_service", "test_user")

    assert password is None


def test_delete_credential_success(mock_keyring):
    """Test successfully deleting a credential."""
    manager = CredentialManager()
    result = manager.delete_credential("test_service", "test_user")

    expected_service_name = f"{WIZFLOW_SERVICE_PREFIX}-test_service"
    mock_keyring.delete_password.assert_called_once_with(expected_service_name, "test_user")
    assert result is True


def test_delete_credential_failure(mock_keyring):
    """Test failure while deleting a credential."""
    from keyring.errors import PasswordDeleteError
    mock_keyring.delete_password.side_effect = PasswordDeleteError("Not found")

    manager = CredentialManager()
    result = manager.delete_credential("test_service", "test_user")

    assert result is False

def test_load_credentials_is_deprecated(caplog):
    """Test that the load_credentials method logs a deprecation warning."""
    # We need to patch keyring here as well to instantiate the manager
    with patch('wizflow.core.credentials.keyring'):
        manager = CredentialManager()
        result = manager.load_credentials()

        assert result == {}
        assert "DEPRECATION WARNING" in caplog.text
