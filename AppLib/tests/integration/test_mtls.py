import pytest
from subservices.mtls.service import MTLSService, MTLSException

def test_mtls_disabled_returns_none():
    svc = MTLSService(enabled=False)
    assert svc.get_ssl_context() is None

def test_mtls_invalid_paths_raises():
    svc = MTLSService(enabled=True, cert_path="notfound.crt", key_path="notfound.key", ca_path="notfound.ca")
    with pytest.raises(MTLSException):
        svc.get_ssl_context()
