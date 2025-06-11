"""
mTLS Subservice

Provides SSL context for mutual TLS (mTLS) connections.
"""

import ssl
import os
from .exceptions import MTLSException

class MTLSService:
    """
    Service for managing mTLS SSL contexts.
    """

    def __init__(self, enabled=False, cert_path=None, key_path=None, ca_path=None):
        """
        Initialize the mTLS service.

        Args:
            enabled (bool): Whether mTLS is enabled.
            cert_path (str): Path to the certificate file.
            key_path (str): Path to the private key file.
            ca_path (str): Path to the CA certificate file.
        """
        self.enabled = enabled
        self.cert_path = cert_path
        self.key_path = key_path
        self.ca_path = ca_path

    def get_ssl_context(self):
        """
        Returns an SSL context for mTLS, or None if mTLS is disabled.

        Raises:
            MTLSException: If mTLS is enabled but configuration is invalid.
        """
        if not self.enabled:
            return None

        # Validate paths
        for path, name in [
            (self.cert_path, "Certificate"),
            (self.key_path, "Key"),
            (self.ca_path, "CA Certificate")
        ]:
            if not path or not os.path.isfile(path):
                raise MTLSException(f"{name} file not found at: {path}")

        try:
            context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            context.load_cert_chain(certfile=self.cert_path, keyfile=self.key_path)
            context.load_verify_locations(cafile=self.ca_path)
            context.verify_mode = ssl.CERT_REQUIRED
            return context
        except Exception as e:
            raise MTLSException(f"Failed to create SSL context: {e}") from e
