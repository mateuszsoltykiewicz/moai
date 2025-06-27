{{/*
serviceaccount

This template defines a Kubernetes ServiceAccount for the application,
with AWS IAM Roles for Service Accounts (IRSA) integration.

- Rendered only if `.Values.serviceAccount.enable` is true.
- The ServiceAccount name and namespace are built from explicit values in values.yaml.
- No defaults are used; all values must be set explicitly.
- Uses an annotation for IRSA integration with AWS.
- Standard labels are included via the "labels" helper template.

Usage: {{ include "serviceaccount" . }}

See: https://docs.aws.amazon.com/eks/latest/userguide/iam-roles-for-service-accounts.html
*/}}

{{- define "serviceaccount" -}}
{{- if .Values.serviceAccount.enable }}

apiVersion: v1
kind: ServiceAccount
metadata:
  # ServiceAccount name is dynamically generated from environment and application names.
  name: {{ printf "%s-%s-serviceaccount" (.Values.environment.name | lower) (.Values.application.name | lower | replace " " "-") | quote }}
  # Namespace for the ServiceAccount, built from environment and namespace names.
  namespace: {{ printf "%s-%s" (.Values.environment.name | lower) (.Values.namespace.name | lower) | quote }}
  labels:
    # Standard labels for resource tracking and selection.
    {{- include "labels" . | nindent 4 }}
    # Application-specific label for identifying the ServiceAccount.
    app.kubernetes.io/name: {{ printf "%s-%s-serviceaccount" (.Values.environment.name | lower) (.Values.application.name | lower | replace " " "-") | quote }}
  annotations:
    # AWS IAM Role ARN for IRSA (IAM Roles for Service Accounts) integration.
    # This allows pods using this ServiceAccount to assume the specified IAM role.
    eks.amazonaws.com/role-arn: "arn:aws:iam::{{ .Values.aws.accountId }}:role/{{ printf "%s-%s-serviceaccount" (.Values.environment.name | lower) (.Values.application.name | lower | replace " " "-") }}"

{{- end }}
{{- end -}}
