# CICD Installer

## Overview

The CICD Installer is a production-grade, Terraform-based solution for deploying and managing Continuous Integration and Continuous Deployment (CICD) tools such as Argo CD, Jenkins, and Tekton on your Kubernetes cluster using Helm charts. It supports environment-specific configuration, Helm values overrides, secure state management, and enables or disables each CICD component dynamically.

---

## Directory Structure

Installer/
└── CiCd/
├── main.tf
├── locals.tf
├── variables.tf
├── run.sh
└── README.md

---

## Features

- **Declarative Deployment:** All CICD tools are defined in a YAML configuration file and managed as code.
- **Dynamic Enable/Disable:** Easily enable or disable any CICD application per environment via the config file.
- **Helm Values Overrides:** Customize Helm chart values for each CICD tool and environment with dedicated values.yaml files.
- **Secure State Management:** Supports both S3 and local backends, with workspace isolation per environment.
- **Consistent Naming:** All resources and workspaces are named following environment and installer conventions.
- **Extensible:** Add or remove CICD components by editing the YAML config—no code changes required.

---

## Configuration

- **YAML configuration files** are located in `Configuration/Installer/CiCd/` per environment.
- **Helm values overrides** are in `Configuration/Helm/{environment}/cicd/{application_name}/values.yaml`.

### Example `cicd.yaml`

see configuration

---

## Usage

Run the `run.sh` script to plan, apply, or destroy the Terraform-managed CICD stack:

./run.sh plan dev
./run.sh apply dev
./run.sh destroy dev

- `<environment>`: The target environment (e.g., dev, prod).
- `[kubeconfig_path]`: (optional) Path to your kubeconfig file.
- `[s3|local]`: (optional) Backend type (default: local).

---

## Naming Conventions

- **Resources:** Named as `<environment>-cicd-<application>`, e.g., `dev-cicd-argocd`.
- **Workspaces:** Named as `<environment>-cicd`.

---

## Helm Values Overrides

- Place custom values for each CICD tool in `Configuration/Helm/{environment}/cicd/{application}/values.yaml`.
- If no override file is provided, the chart’s default values are used.

---

## State Management

- **S3 backend:** For production, state is stored in an S3 bucket (with native S3 locking).
- **Local backend:** For development, state is stored locally in `.terraform-state/`.
- **Workspaces:** Each environment uses its own Terraform workspace for isolation.

---

## Best Practices

- **Validate YAML configuration** before applying (schema validation is supported in `run.sh`).
- **Pin chart versions** for reproducible deployments.
- **Use secure credentials** for S3 and Kubernetes access.
- **Keep Helm charts and values files under version control.**
- **Enable only required CICD tools** in each environment.

---

## Troubleshooting

- Check Terraform and Helm logs for errors.
- Ensure all referenced Helm values files exist and are valid YAML.
- Validate your YAML config with schema tools before deployment.
- Confirm your kubeconfig and permissions are correct.

---

## References

- [Terraform Helm Provider](https://registry.terraform.io/providers/hashicorp/helm/latest/docs)
- [Helm Documentation](https://helm.sh/docs/)
- [Argo CD Helm Chart](https://github.com/argoproj/argo-helm)
- [Tekton Helm Chart](https://tekton.dev/charts/)
- [YAML Schema Validation](https://github.com/23andMe/Yamale)

---

## Extending the Installer

- Add new CICD tools by appending to `cicd.yaml`.
- Create a new values.yaml override file for each new tool as needed.
- Adjust `run.sh` and Terraform variable files if you add new required parameters.

---

This installer is designed for production resilience, maintainability, and easy extensibility in modern Kubernetes environments.
