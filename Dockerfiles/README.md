# Dockerfiles Directory

## Overview

This directory contains Dockerfiles and README.md files for each microservice in the platform. Each Dockerfile is designed to build a production-grade, minimal, and secure container image for its respective microservice.

## Structure

- Each microservice has its own subdirectory under `/Dockerfiles`.
- Each subdirectory contains a `Dockerfile` and a `README.md` specific to that microservice.

## Dockerfile Features

- Multi-stage builds to minimize image size and separate build/runtime dependencies.
- Alpine Linux base images for minimal footprint and security.
- Installation of system dependencies via `apk` package manager.
- Python dependencies installed via `pip`.
- Use of non-root user for security.
- Metadata labels for maintainability and traceability.
- Exposed ports as required by each microservice.
- Entrypoint and CMD configured to run the microservice with Uvicorn.
- No environment variables set in Dockerfiles; configuration is managed externally via Kubernetes ConfigMaps and Secrets.

## Usage

### Building an Image

docker build -t {microservice-name}:1.0.0 -f Dockerfiles/{MicroServiceName}/Dockerfile .

### Running a Container

docker run -d
--name {microservice-name}
-p 8000:8000
-v ./config:/app/config
{microservice-name}:1.0.0

For hardware-specific microservices (e.g., I2CAdapter, CANBusAdapter), additional device permissions and mounts are required.

## Best Practices

- Use Kubernetes for orchestration and manage environment variables via ConfigMaps and Secrets.
- Implement resource limits and health probes in Kubernetes deployments.
- Regularly rebuild and scan images for vulnerabilities.
- Maintain consistent directory and Dockerfile structure across all microservices.

## Contact

For questions or support, please contact the platform engineering team.
