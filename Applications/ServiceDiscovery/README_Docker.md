# ServiceDiscovery Docker Image

This Dockerfile builds a production-grade, minimal, and secure image for the ServiceDiscovery microservice.

## Build

docker build -t service-discovery:1.0.0 -f Dockerfiles/ServiceDiscovery/Dockerfile .

## Run

docker run -d
--name service-discovery
-p 8000:8000
-v ./config:/app/config
service-discovery:1.0.0

## Ports

- **8000**: Default FastAPI/Uvicorn port

## Kubernetes & Service Registry Integration

- The image is ready for use with Kubernetes and Vault.
- ServiceDiscovery will interact with the Kubernetes API for service listing and with Vault for the allowed service list.
- For advanced service discovery patterns (client-side, server-side, DNS-based, or library-based), see [Solo.io][1], [F5][2], [Ambassador][3], and [Kong][5] for architectural best practices.

## Security

- Runs as a non-root user (`appuser`)
- No secrets or environment variables are set in the Dockerfile (use Kubernetes ConfigMaps/Secrets)
- Minimal runtime dependencies (Alpine Linux base)

## Best Practices

- Use Kubernetes for orchestration and set environment variables via ConfigMap/Secret
- Use resource limits in production deployments
- Implement liveness and readiness probes in your K8s manifests
- Regularly rebuild and scan images for vulnerabilities
- Audit service registry and allowed list regularly ([5])

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
- [1]: https://www.solo.io/topics/microservices/microservices-service-discovery  
- [2]: https://www.f5.com/fr_fr/company/blog/nginx/service-discovery-in-a-microservices-architecture  
- [3]: https://www.getambassador.io/blog/service-discovery-microservices  
- [5]: https://konghq.com/blog/learning-center/service-discovery-in-a-microservices-architecture  
