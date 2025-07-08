# Platform Installer

## Overview

The Platform Installer manages the deployment of core platform services (Ingress, CertManager, DockerRepository, Istio, Keycloak, Vault, Strimzi Topic Operator, etc.) on your Kubernetes cluster using Terraform and Helm. It supports environment-specific configuration, Helm values overrides, and resource naming conventions.

## Directory Structure

Platform/
├── main.tf
├── locals.tf
├── modules/
│   ├── ingress/
│   ├── cert-manager/
│   ├── docker-repository/
│   ├── istio/
│   ├── keycloak/
│   ├── vault/
│   ├── strimzi-topic-operator/
│   └── ...
├── run.sh
└── README.md

## Features

- Declarative deployment of platform services via Helm charts.
- Environment-specific configuration using YAML files.
- Helm values overrides per environment and module.
- Dynamic enable/disable of modules based on configuration.
- Consistent naming conventions for resources and workspaces.

## Configuration

- Configuration files are located in `Configuration/Installer/Platform/` per environment.
- Helm values overrides are in `Configuration/Helm/{environment}/platform/{module}/values.yaml`.
- Example configuration file (`platform.yaml`):

platform:

  /- name: ingress
    enabled: true
    chart: ./modules/ingress
    version: 1.9.0
    values_file: ../../Configuration/Helm/dev/platform/ingress/values.yaml

  /- name: cert-manager
    enabled: true
    chart: ./modules/cert-manager
    version: 1.13.2
    values_file: ../../Configuration/Helm/dev/platform/cert-manager/values.yaml

  /- name: strimzi-topic-operator
    enabled: true
    chart: ./modules/strimzi-topic-operator
    version: 0.39.0
    values_file: ../../Configuration/Helm/dev/platform/strimzi-topic-operator/values.yaml

## Usage

Run the `run.sh` script to plan, apply, or destroy the platform stack:

./run.sh plan dev
./run.sh apply dev
./run.sh destroy dev

## Naming Conventions

- Resource names are prefixed with the environment and installer type, e.g., `dev-platform-ingress`.
- Terraform workspaces follow the pattern `<environment>-platform`.

## Helm Values Overrides

- Helm values files allow customization of chart parameters per environment and module.
- If no override file is provided, default chart values are used.

## Best Practices

- Validate configuration YAML files before applying.
- Use strong naming conventions to avoid resource conflicts.
- Keep Helm charts and modules up to date.
- Enable only required modules per environment.

## Troubleshooting

- Check Terraform logs for errors.
- Validate YAML configuration files with schema validators.
- Ensure Helm values files are correctly referenced.

## References

- [Terraform Helm Provider](https://registry.terraform.io/providers/hashicorp/helm/latest/docs)
- [Helm Documentation](https://helm.sh/docs/)
- [YAML Schema Validation](https://github.com/23andMe/Yamale)
