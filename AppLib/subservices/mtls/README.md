# mTLS Subservice

## Overview

This subservice provides tools for enabling mutual TLS (mTLS) in Python services.  
It is designed to be compatible with future integration with cert-manager and Istio, but works with any certificate source.

## Features

- Loads certificates and keys from configurable paths
- Returns an `ssl.SSLContext` object for use in HTTP/gRPC servers or clients
- Can be enabled or disabled via configuration
- Fails gracefully if mTLS is disabled or misconfigured
- Ready for future extension (e.g., hot-reloading certificates)

## Configuration

| Variable         | Description                      | Example Path           |
|------------------|----------------------------------|------------------------|
| `mtls_enabled`   | Enable/disable mTLS (bool)       | `true` or `false`      |
| `cert_path`      | Path to certificate file         | `/etc/certs/tls.crt`   |
| `key_path`       | Path to private key file         | `/etc/certs/tls.key`   |
| `ca_path`        | Path to CA certificate file      | `/etc/certs/ca.crt`    |

## Usage

from subservices.mtls.service import MTLSService, MTLSException
mtls = MTLSService(
  enabled=True,
  cert_path=”/etc/certs/tls.crt”,
  key_path=”/etc/certs/tls.key”,
  ca_path=”/etc/certs/ca.crt” )
  ssl_context = mtls.get_ssl_context()

