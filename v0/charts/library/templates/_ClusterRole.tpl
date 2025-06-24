{{/*
clusterrole

This template defines a Kubernetes ClusterRole for the application.

The ClusterRole rules and name can be fully configured via values.yaml.

Usage: {{ include "clusterrole" . }}
*/}}

{{- define "clusterrole" -}}
{{- if .Values.clusterRole.enable }}

apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  # Name is generated from environment.name and application.name for clarity and uniqueness.
  name: {{ printf "%s-%s-clusterrole" (.Values.environment.name | lower | replace " " "-") (.Values.application.name | lower | replace " " "-") | quote }}
  labels:
    {{- include "labels" . | nindent 4 }}

rules:
{{- if .Values.clusterRole.rules }}
  {{- toYaml .Values.clusterRole.rules | nindent 2 }}
{{- else }}
  # Default: read-only access to Secrets and ConfigMaps in all namespaces.
  - apiGroups: [""]
    resources: ["secrets", "configmaps"]
    verbs: ["get", "list"]
{{- end }}

{{- end }}
{{- end -}}
