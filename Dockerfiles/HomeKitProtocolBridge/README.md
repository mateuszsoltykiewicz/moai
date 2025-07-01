# HomeKitProtocolBridge Docker Image

This Dockerfile builds a production-grade, minimal, and secure image for the HomeKitProtocolBridge microservice, supporting HAP-python and mDNS/Bonjour.

## Build

docker build -t homekit-protocol-bridge:1.0.0 -f Dockerfiles/HomeKitProtocolBridge/Dockerfile .

## Run

docker run -d
--name homekit-protocol-bridge
-p 51826:51826
-v ./config:/app/config
homekit-protocol-bridge:1.0.0

## Ports

- **51826**: Default HomeKit Accessory Protocol (HAP) port

## mDNS/Bonjour Support

- The image includes Avahi for mDNS/Bonjour service discovery, required for HomeKit compatibility.
- If running on Kubernetes, ensure your cluster/network supports multicast/mDNS.

## Security

- Runs as a non-root user (`appuser`)
- No secrets or environment variables are set in the Dockerfile (use Kubernetes ConfigMaps/Secrets)
- Minimal runtime dependencies (Alpine Linux base)

## Best Practices

- Use Kubernetes for orchestration and set environment variables via ConfigMap/Secret
- Use resource limits in production deployments
- Implement liveness and readiness probes in your K8s manifests
- Regularly rebuild and scan images for vulnerabilities

## Multi-Stage Build

- **Builder stage**: Installs all build dependencies and Python packages
- **Runtime stage**: Copies only runtime essentials, minimizing image size and attack surface

## Metadata

- Maintainer and version labels included for traceability

## Updating

- Update `requirements.txt` as needed for dependency changes
- Rebuild the image after code or dependency updates

---

For further details, see the platform-level deployment and security documentation.
