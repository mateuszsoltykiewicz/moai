# mTLS Component (Deprecated)

## Overview

**This component is deprecated and no longer required.**

Mutual TLS (mTLS) is now enforced at the service mesh layer using [Istio](https://istio.io/), which provides automatic certificate management and encrypted service-to-service communication.

## Migration

- All mTLS functionality is handled by Istio and does not require application-level code.
- Remove any dependencies on `Library/mtls` from your services.
- Ensure your services are deployed within the Istio mesh and that mTLS is enabled via Istio policies.

## Security

- All in-cluster traffic is transparently encrypted and authenticated by Istio.
- mTLS policies are managed centrally via Istio configuration.

## Last Updated

2025-06-28
