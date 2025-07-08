#!/bin/bash
set -euo pipefail

ACTION="${1:-plan}"
ENV_NAME="${2:-dev}"
INSTALLER_TYPE="cicd"
BACKEND_TYPE="${3:-local}"

WORKSPACE="${ENV_NAME}-${INSTALLER_TYPE}"

if [[ "$BACKEND_TYPE" == "s3" ]]; then
  BUCKET="podgrzewacz-${ENV_NAME}-terraform-state"
  REGION="eu-central-1"
  KEY="${INSTALLER_TYPE}/terraform.tfstate"
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
# yamale -s ../../Configuration/Installer/${INSTALLER_TYPE}/schema.yaml ../../Configuration/Installer/${INSTALLER_TYPE}/${ENV_NAME}.yaml || {
#   echo "YAML validation failed. Aborting."
#   exit 1
# }

if [[ "$ACTION" == "plan" ]]; then
  terraform plan -var="environment=$ENV_NAME" -var="installer_type=$INSTALLER_TYPE"
elif [[ "$ACTION" == "apply" ]]; then
  terraform apply -auto-approve -var="environment=$ENV_NAME" -var="installer_type=$INSTALLER_TYPE"
elif [[ "$ACTION" == "destroy" ]]; then
  terraform destroy -auto-approve -var="environment=$ENV_NAME" -var="installer_type=$INSTALLER_TYPE"
else
  echo "Usage: $0 {plan|apply|destroy} <environment> [s3|local]"
  exit 1
fi
