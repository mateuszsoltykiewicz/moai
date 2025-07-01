# CANBusAdapter Docker Image

This Dockerfile builds a production-grade, minimal, and secure image for the CANBusAdapter microservice, with hardware support for CAN and I2C operations.

## Build

docker build -t canbus-adapter:1.0.0 -f Dockerfiles/CANBusAdapter/Dockerfile .


## Run

docker run -d
--name canbus-adapter
-p 8000:8000
--device /dev/i2c-1
--device /dev/can0
--cap-add=SYS_RAWIO
canbus-adapter:1.0.0


## Ports

- **8000**: Default FastAPI/Uvicorn port

## Hardware Access

- Requires access to `/dev/i2c-1` and `/dev/can0` (or your system’s CAN/I2C devices)
- Use `--device` and `--cap-add` flags as shown above
- For Kubernetes, use device plugins or securityContext as appropriate

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
