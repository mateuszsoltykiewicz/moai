# <InstallerType> Installer

## Purpose
Manages the deployment of <InstallerType> components using Terraform and Helm.

## Directory Structure
- main.tf: Root Terraform configuration
- locals.tf: Naming, tags, and locals
- modules/: Reusable modules for this installer
- run.sh: Bootstrap and automation script
- README.md: This documentation

## Usage

cd Installer/<InstallerType>
./run.sh plan <env> [s3|local]
./run.sh apply <env> [s3|local]
./run.sh destroy <env> [s3|local]


- `<env>`: Environment name (e.g., dev, prod)
- `[s3|local]`: Backend type (default: local)

## Naming Conventions

- All resources are named `<env>-<installer-type>-<module>`
- Workspaces: `<env>-<installer-type>`

## State Management

- S3 backend for production, local backend for development/lab
- State files are isolated per environment and installer

## Configuration

- Environment-specific YAML in `../../Configuration/Installer/<InstallerType>/`
- Optional Helm values overrides in `../../Configuration/Helm/<ModuleType>/`
