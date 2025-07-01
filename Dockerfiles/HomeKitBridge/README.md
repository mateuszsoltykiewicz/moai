# HomeKitBridge Docker Image

This Dockerfile builds a production-grade, minimal, and secure image for the HomeKitBridge microservice.

## Build

docker build -t homekit-bridge:1.0.0 -f Dockerfiles/HomeKitBridge/Dockerfile .

## Run

docker run -d
--name homekit-bridge
-p 8000:8000
-v ./config:/app/config
homekit-bridge:1.0.0

## Ports

- **8000**: Default FastAPI/Uvicorn port

## mDNS/Bonjour Support

- The image includes Avahi for mDNS/Bonjour service discovery, which is required for HomeKit compatibility ([2], [5]).
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

---

**References:**
- [Home Assistant HomeKit Bridge Best Practices][1]
- [Home Assistant HomeKit Integration][2]
- [zebin-wu/homekit-bridge (embedded)][5]

[1]: https://community.home-assistant.io/t/best-practices-for-homekit-bridge-configuration/828094
[2]: https://www.home-assistant.io/integrations/homekit/
[5]: https://github.com/zebin-wu/homekit-bridge
