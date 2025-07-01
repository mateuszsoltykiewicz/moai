# SecretsRotator Docker Image

This Dockerfile builds a production-grade, minimal, and secure image for the SecretsRotator microservice.

## Build

docker build -t secrets-rotator:1.0.0 -f Dockerfiles/SecretsRotator/Dockerfile .

## Run

docker run -d
--name secrets-rotator
-p 8000:8000
-v ./config:/app/config
secrets-rotator:1.0.0

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
- Rotate secrets regularly and audit usage ([2], [5])

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

- [Docker Secrets best practices][2]  
- [Microsoft Engineering Playbook: Secrets Rotation][5]  
- [Gruntwork: Production-Grade Architecture][4]  
- [DZone: Microservice README Best Practices][3]

[2]: https://betterstack.com/community/guides/scaling-docker/docker-secrets/
[3]: https://dzone.com/articles/a-readme-for-your-microservice-github-repository
[4]: https://www.gruntwork.io/blog/how-to-build-an-end-to-end-production-grade-architecture-on-aws-part-2
[5]: https://microsoft.github.io/code-with-engineering-playbook/CI-CD/dev-sec-ops/secrets-management/secrets_rotation/
