"""Secure credential storage using OS keyring"""
import keyring
from typing import Optional
from loguru import logger


SERVICE_NAME = "jira-cli"
DOMAIN_KEY = "jira_domain"
EMAIL_KEY = "jira_email"
TOKEN_KEY = "jira_api_token"


class CredentialStorage:
    """Handles secure credential storage and retrieval"""

    @staticmethod
    def store_credentials(domain: str, email: str, api_token: str) -> None:
        """
        Store Jira credentials securely in the system keyring.
        
        Args:
            domain: Jira domain (e.g., your-domain.atlassian.net)
            email: Email associated with Jira account
            api_token: API token for authentication
        """
        try:
            keyring.set_password(SERVICE_NAME, DOMAIN_KEY, domain)
            keyring.set_password(SERVICE_NAME, EMAIL_KEY, email)
            keyring.set_password(SERVICE_NAME, TOKEN_KEY, api_token)
            logger.debug("Credentials stored successfully")
        except Exception as e:
            logger.error(f"Failed to store credentials: {e}")
            raise

    @staticmethod
    def get_credentials() -> Optional[tuple[str, str, str]]:
        """
        Retrieve stored credentials from the system keyring.
        
        Returns:
            Tuple of (domain, email, api_token) if all credentials exist, None otherwise
        """
        try:
            domain = keyring.get_password(SERVICE_NAME, DOMAIN_KEY)
            email = keyring.get_password(SERVICE_NAME, EMAIL_KEY)
            api_token = keyring.get_password(SERVICE_NAME, TOKEN_KEY)
            
            if domain and email and api_token:
                logger.debug("Credentials retrieved from keyring")
                return (domain, email, api_token)
            
            logger.debug("No complete credentials found in keyring")
            return None
        except Exception as e:
            logger.error(f"Failed to retrieve credentials: {e}")
            return None

    @staticmethod
    def delete_credentials() -> None:
        """Delete all stored credentials from the system keyring."""
        try:
            keyring.delete_password(SERVICE_NAME, DOMAIN_KEY)
        except keyring.errors.PasswordDeleteError:
            logger.debug("Domain not found in keyring")
        except Exception as e:
            logger.warning(f"Error deleting domain: {e}")

        try:
            keyring.delete_password(SERVICE_NAME, EMAIL_KEY)
        except keyring.errors.PasswordDeleteError:
            logger.debug("Email not found in keyring")
        except Exception as e:
            logger.warning(f"Error deleting email: {e}")

        try:
            keyring.delete_password(SERVICE_NAME, TOKEN_KEY)
        except keyring.errors.PasswordDeleteError:
            logger.debug("Token not found in keyring")
        except Exception as e:
            logger.warning(f"Error deleting token: {e}")

        logger.debug("Credentials deleted from keyring")

    @staticmethod
    def has_credentials() -> bool:
        """
        Check if credentials are stored in the keyring.
        
        Returns:
            True if all credentials exist, False otherwise
        """
        credentials = CredentialStorage.get_credentials()
        return credentials is not None
