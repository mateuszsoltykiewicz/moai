{{/*
role

This template defines a Kubernetes Role for the application.

- The Role's name and rules are fully configured via values.yaml.
- No defaults are used; all values must be set explicitly.
- Naming follows the pattern: <environment>-<application>-role.
- Namespace follows the pattern: <environment>-<namespace>.
- Standard labels are included via the "labels" helper template.

Usage: {{ include "role" . }}
*/}}

{{- define "role" -}}
{{- if .Values.role.enable }}

apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  # Namespace for the Role, built from environment and namespace names.
  namespace: "{{ .Values.environment.name | lower }}-{{ .Values.namespace.name | lower }}"
  # Role name, built from environment and application names.
  name: {{ printf "%s-%s-role" (.Values.environment.name | lower) (.Values.application.name | lower | replace " " "-") | quote }}
  labels:
    {{- include "labels" . | nindent 4 }}

rules:
{{- if .Values.role.rules }}
  {{- toYaml .Values.role.rules | nindent 2 }}
{{- else }}
  # Default: read-only access to ConfigMaps and Secrets in the namespace.
  - apiGroups: [""]
    resources: ["configmaps", "secrets"]
    verbs: ["get", "list"]
{{- end }}

{{- end }}
{{- end -}}
