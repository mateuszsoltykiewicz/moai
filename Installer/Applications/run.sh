#!/bin/bash
set -euo pipefail

ACTION="${1:-plan}"
ENV_NAME="${2:-dev}"
KUBECONFIG_PATH="${3:-$HOME/.kube/config}"
CONFIG_PATH="../../Configuration/Installer/Applications/apps.yaml"
BACKEND_TYPE="${4:-local}"
WORKSPACE="${ENV_NAME}-applications"

# Backend config (S3 or local)
if [[ "$BACKEND_TYPE" == "s3" ]]; then
  BUCKET="podgrzewacz-${ENV_NAME}-terraform-state"
  REGION="eu-central-1"
  KEY="applications/terraform.tfstate"
  cat > backend.tf <<EOF
terraform {
  backend "s3" {
    bucket         = "$BUCKET"
    key            = "$KEY"
    region         = "$REGION"
  }
}
EOF
else
  mkdir -p .terraform-state
  cat > backend.tf <<EOF
terraform {
  backend "local" {
    path = ".terraform-state/${WORKSPACE}.tfstate"
  }
}
EOF
fi

terraform init -reconfigure

terraform workspace select "$WORKSPACE" || terraform workspace new "$WORKSPACE"

echo "Validating configuration..."
# yamale -s ../../Configuration/Installer/Applications/schema.yaml $CONFIG_PATH || {
#   echo "YAML validation failed. Aborting."
#   exit 1
# }

if [[ "$ACTION" == "plan" ]]; then
  terraform plan -var="environment=$ENV_NAME" \
    -var="apps_config_path=$CONFIG_PATH" \
    -var="kubeconfig_path=$KUBECONFIG_PATH"
elif [[ "$ACTION" == "apply" ]]; then
  terraform apply -auto-approve -var="environment=$ENV_NAME" \
    -var="apps_config_path=$CONFIG_PATH" \
    -var="kubeconfig_path=$KUBECONFIG_PATH"
elif [[ "$ACTION" == "destroy" ]]; then
  terraform destroy -auto-approve -var="environment=$ENV_NAME" \
    -var="apps_config_path=$CONFIG_PATH" \
    -var="kubeconfig_path=$KUBECONFIG_PATH"
else
  echo "Usage: $0 {plan|apply|destroy} <environment> [kubeconfig_path] [s3|local]"
  exit 1
fi
