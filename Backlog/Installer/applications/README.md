# Applications Installer

## Overview

The Applications Installer manages the deployment of all application-level microservices on the Kubernetes cluster using Terraform and Helm. It supports environment-specific configuration, Helm values overrides, and image digest management for immutable deployments.

## Directory Structure


## Features

- Declarative deployment of applications via Helm charts.
- Environment-specific configuration using YAML files.
- Support for Helm values overrides per application and environment.
- Image digest support for immutable container images.
- Dynamic enable/disable of applications based on configuration.
- Consistent naming conventions for resources and workspaces.

## Configuration

- Configuration files are located in `Configuration/Installer/Applications/` per environment.
- Helm values overrides are located in `Configuration/Helm/{environment}/applications/{application_name}/values.yaml`.
- Example configuration file (`apps.yaml`):

apps:
  name: alarms-server
  enabled: true
  namespace: platform
  chart: ./modules/alarms-server
  version: 1.2.3
  values_file: ../../Configuration/Helm/dev/applications/alarms-server/values.yaml
  image_digest: "sha256:abcdef123..."
  variables:
  replicaCount: 2
  image_tag: "v1.2.3"

  name: state-server
  enabled: false

## Usage

Run the `run.sh` script to plan, apply, or destroy the Terraform-managed applications:

./run.sh plan dev
./run.sh apply dev
./run.sh destroy dev

## Naming Conventions

- Resource names are prefixed with the environment and installer type, e.g., `dev-applications-alarms-server`.
- Terraform workspaces follow the pattern `<environment>-applications`.

## Helm Values Overrides

- Helm values files allow customization of chart parameters per environment and application.
- If no override file is provided, default chart values are used.

## Image Digest Support

- Image digests ensure immutable deployments by referencing exact image versions.
- The digest is passed as a Helm value and used in the deployment manifests.

## Best Practices

- Validate configuration YAML files before applying.
- Use strong naming conventions to avoid resource conflicts.
- Keep Helm charts and modules up to date.
- Use the image digest feature to avoid deployment drift.

## Troubleshooting

- Check Terraform logs for errors.
- Validate YAML configuration files with schema validators.
- Ensure Helm values files are correctly referenced.

## References

- [Terraform Helm Provider](https://registry.terraform.io/providers/hashicorp/helm/latest/docs)
- [Helm Documentation](https://helm.sh/docs/)
- [YAML Schema Validation](https://github.com/23andMe/Yamale)
