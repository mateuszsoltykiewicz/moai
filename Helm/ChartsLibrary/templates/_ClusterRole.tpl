{{/*
clusterrole

Defines a Kubernetes ClusterRole for the application.
- Name: DNS-1123 compliant, max 63 chars, lowercase, hyphens only.
- Rules: configurable via values.yaml, with a secure read-only default.
- Usage: {{ include "charts-library.clusterrole" . }}
*/}}

{{- define "charts-library.clusterrole" -}}
{{- if .Values.clusterRole.enable }}

apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: {{ include "charts-library.clusterroleName" . }}
  labels:
    {{- include "charts-library.labels" . | nindent 4 }}

rules:
{{- if and .Values.clusterRole.rules (gt (len .Values.clusterRole.rules) 0) }}
  {{- toYaml .Values.clusterRole.rules | nindent 2 }}
{{- else }}
  # Default: read-only access to Secrets and ConfigMaps in all namespaces.
  - apiGroups: [""]
    resources: ["secrets", "configmaps"]
    verbs: ["get", "list"]
{{- end }}

{{- end }}
{{- end -}}

{{/*
Helper for DNS-1123-compliant ClusterRole name.
*/}}
{{- define "charts-library.clusterroleName" -}}
{{- $env := default "default" .Values.environment.name | lower | regexReplaceAll "[^a-z0-9-]" "-" | trunc 20 | trimSuffix "-" -}}
{{- $app := default "app" .Values.application.name | lower | regexReplaceAll "[^a-z0-9-]" "-" | trunc 30 | trimSuffix "-" -}}
{{- printf "%s-%s-clusterrole" $env $app | trunc 63 | trimSuffix "-" -}}
{{- end }}
