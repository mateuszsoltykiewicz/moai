{{/*
charts-library.role

Defines a Kubernetes Role for the application.
- Name/namespace: DNS-1123 compliant, max 63 chars.
- Usage: {{ include "charts-library.role" . }}
*/}}

{{- define "charts-library.role" -}}
{{- if .Values.role.enable }}

{{- $env := default "default" .Values.environment.name | lower | regexReplaceAll "[^a-z0-9-]" "-" | trunc 20 | trimSuffix "-" -}}
{{- $ns := default "default" .Values.namespace.name | lower | regexReplaceAll "[^a-z0-9-]" "-" | trunc 30 | trimSuffix "-" -}}
{{- $app := default "app" .Values.application.name | lower | regexReplaceAll "[^a-z0-9-]" "-" | trunc 30 | trimSuffix "-" -}}
{{- $roleName := printf "%s-%s-role" $env $app | trunc 63 | trimSuffix "-" -}}
{{- $namespace := printf "%s-%s" $env $ns | trunc 63 | trimSuffix "-" -}}

apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: {{ $namespace }}
  name: {{ $roleName }}
  labels:
    {{- include "charts-library.labels" . | nindent 4 }}

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
