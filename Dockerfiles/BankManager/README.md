# BankManager Docker Image

This Dockerfile builds a production-grade, minimal, and secure image for the BankManager microservice.

## Build

docker build -t bank-manager:1.0.0 -f Dockerfiles/BankManager/Dockerfile .


## Run

docker run -d
--name bank-manager
-p 8000:8000
-v ./config:/app/config
bank-manager:1.0.0


## Ports

- **8000**: Default FastAPI/Uvicorn port

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
