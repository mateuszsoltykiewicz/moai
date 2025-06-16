import ssl
from pathlib import Path
from typing import Optional
from core.config import AsyncConfigManager
from core.exceptions import mTLSException
from core.logging import get_logger
from metrics.mtls import MTLS_CERT_EXPIRY, MTLS_ERRORS
from datetime import datetime
from cryptography import x509
from cryptography.hazmat.backends import default_backend

logger = get_logger(__name__)

class MTLSAdapter:
    def __init__(self, config_manager: AsyncConfigManager):
        self.config_manager = config_manager
        self._ssl_context: Optional[ssl.SSLContext] = None
        self._cert_expiry: Optional[datetime] = None

    async def load_certificates(self):
        """Load certs from paths (mounted from cert-manager secret)."""
        config = await self.config_manager.get()
        cert_path = Path(config.mtls.cert_path)
        key_path = Path(config.mtls.key_path)
        ca_path = Path(config.mtls.ca_path)
        try:
            context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            context.load_cert_chain(certfile=str(cert_path), keyfile=str(key_path))
            context.load_verify_locations(cafile=str(ca_path))
            context.verify_mode = ssl.CERT_REQUIRED
            self._ssl_context = context
            self._cert_expiry = self._get_cert_expiry(cert_path)
            MTLS_CERT_EXPIRY.set((self._cert_expiry - datetime.utcnow()).total_seconds())
            logger.info("mTLS certificates loaded and SSL context created")
        except Exception as e:
            MTLS_ERRORS.labels(error_type="filesystem_load").inc()
            logger.error(f"Failed to load mTLS certs: {e}")
            raise mTLSException("Failed to load mTLS certificates") from e

    def get_ssl_context(self) -> ssl.SSLContext:
        if not self._ssl_context:
            raise mTLSException("SSL context not initialized")
        return self._ssl_context

    def _get_cert_expiry(self, cert_path: Path) -> datetime:
        with open(cert_path, "rb") as f:
            cert = x509.load_pem_x509_certificate(f.read(), default_backend())
            return cert.not_valid_after

    async def health_check(self) -> dict:
        try:
            if not self._ssl_context or not self._cert_expiry:
                await self.load_certificates()
            remaining = (self._cert_expiry - datetime.utcnow()).days
            return {
                "valid": True,
                "expiry": self._cert_expiry.isoformat(),
                "remaining_days": remaining
            }
        except Exception as e:
            MTLS_ERRORS.labels(error_type="health_check").inc()
            return {
                "valid": False,
                "error": str(e),
                "remaining_days": 0
            }
