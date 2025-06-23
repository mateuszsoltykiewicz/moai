"""
MtlsManager: Centralized mTLS configuration and enforcement.

- Manages mTLS certificate loading, validation, and enforcement
- Supports Kubernetes cert-manager integration (cert injection via volume)
- Optionally enforces mTLS for all or selected API endpoints
- Integrates with metrics and logging
"""

import ssl
from typing import Optional, Dict, Any
from .schemas import MtlsConfig
from .exceptions import MtlsConfigError
from .metrics import record_mtls_operation
from .utils import log_info

class MtlsManager:
    def __init__(self, config: MtlsConfig):
        self._config = config
        self._ssl_context: Optional[ssl.SSLContext] = None

    def setup(self):
        """
        Load certificates and configure SSL context for mTLS.
        """
        try:
            context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            context.load_cert_chain(
                certfile=self._config.server_cert,
                keyfile=self._config.server_key
            )
            context.load_verify_locations(self._config.ca_cert)
            context.verify_mode = ssl.CERT_REQUIRED if self._config.enforce else ssl.CERT_OPTIONAL
            self._ssl_context = context
            record_mtls_operation("setup")
            log_info("MtlsManager: SSL context configured for mTLS.")
        except Exception as e:
            raise MtlsConfigError(f"Failed to configure mTLS: {e}")

    def get_ssl_context(self) -> Optional[ssl.SSLContext]:
        """
        Return the configured SSL context, or None if not enforcing mTLS.
        """
        return self._ssl_context if self._config.enforce else None

    def is_enforced(self) -> bool:
        return self._config.enforce

    def get_cert_info(self) -> Dict[str, Any]:
        """
        Return info about loaded certificates (for diagnostics).
        """
        return {
            "server_cert": self._config.server_cert,
            "server_key": self._config.server_key,
            "ca_cert": self._config.ca_cert,
            "enforce": self._config.enforce
        }
