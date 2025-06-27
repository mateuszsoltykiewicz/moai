"""
Production-grade mTLS manager with async reload, certificate validation, and enhanced security.
"""

import ssl
import asyncio
from typing import Optional, Dict, Any
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from .schemas import MtlsConfig
from .exceptions import MtlsConfigError, MtlsCertValidationError
from .metrics import record_mtls_operation
from .utils import log_info, log_error, log_debug

class MtlsManager:
    def __init__(self, config: MtlsConfig):
        self._config = config
        self._ssl_context: Optional[ssl.SSLContext] = None
        self._enforce = config.enforce
        self._cert_info: Dict[str, Any] = {}
        self._lock = asyncio.Lock()

    async def setup(self):
        """Async certificate loading with validation"""
        async with self._lock:
            try:
                await self._load_certificates()
                record_mtls_operation("setup")
                log_info("mTLS: SSL context configured")
            except Exception as e:
                log_error(f"mTLS setup failed: {e}")
                raise MtlsConfigError(f"mTLS setup failed: {e}")

    async def reload(self):
        """Hot-reload certificates without downtime"""
        async with self._lock:
            try:
                await self._load_certificates()
                record_mtls_operation("reload")
                log_info("mTLS: Certificates reloaded")
            except Exception as e:
                log_error(f"Certificate reload failed: {e}")

    async def _load_certificates(self):
        """Load and validate certificates with detailed metadata"""
        context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        
        # Load server cert with async file reading
        server_cert = await self._read_file(self._config.server_cert)
        server_key = await self._read_file(self._config.server_key)
        ca_cert = await self._read_file(self._config.ca_cert)
        
        # Parse certificates for metadata
        self._cert_info = {
            "server": self._parse_cert(server_cert),
            "ca": self._parse_cert(ca_cert),
            "enforce": self._enforce
        }
        
        # Load into context
        context.load_cert_chain(
            certfile=self._config.server_cert,
            keyfile=self._config.server_key
        )
        context.load_verify_locations(cadata=ca_cert)
        context.verify_mode = ssl.CERT_REQUIRED if self._enforce else ssl.CERT_OPTIONAL
        self._ssl_context = context

    async def _read_file(self, path: str) -> str:
        """Async file reading with error handling"""
        try:
            async with asyncio.open_file(path, "r") as f:
                return await f.read()
        except Exception as e:
            log_error(f"File read error ({path}): {e}")
            raise MtlsConfigError(f"File read failed: {path}")

    def _parse_cert(self, pem_data: str) -> Dict[str, Any]:
        """Extract certificate details with cryptography"""
        try:
            cert = x509.load_pem_x509_certificate(pem_data.encode(), default_backend())
            return {
                "subject": cert.subject.rfc4514_string(),
                "issuer": cert.issuer.rfc4514_string(),
                "not_valid_before": cert.not_valid_before.isoformat(),
                "not_valid_after": cert.not_valid_after.isoformat(),
                "serial_number": str(cert.serial_number),
                "signature_algorithm": cert.signature_algorithm_oid._name
            }
        except Exception as e:
            log_error(f"Certificate parsing error: {e}")
            raise MtlsCertValidationError("Invalid certificate format")

    async def set_enforce(self, enforce: bool):
        """Update enforcement mode thread-safely"""
        async with self._lock:
            self._enforce = enforce
            if self._ssl_context:
                self._ssl_context.verify_mode = ssl.CERT_REQUIRED if enforce else ssl.CERT_OPTIONAL
            record_mtls_operation("enforce_toggle")
            log_info(f"mTLS enforcement set to: {enforce}")

    def get_ssl_context(self) -> Optional[ssl.SSLContext]:
        return self._ssl_context if self._enforce else None

    def is_enforced(self) -> bool:
        return self._enforce

    def get_cert_info(self) -> Dict[str, Any]:
        return self._cert_info
