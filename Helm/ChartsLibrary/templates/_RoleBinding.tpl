{{/*
charts-library.rolebinding

Defines a Kubernetes RoleBinding for the application.
- Name/namespace: DNS-1123 compliant, max 63 chars.
- Usage: {{ include "charts-library.rolebinding" . }}
*/}}

{{- define "charts-library.rolebinding" -}}
{{- if .Values.role.enable }}

{{- $env := default "default" .Values.environment.name | lower | regexReplaceAll "[^a-z0-9-]" "-" | trunc 20 | trimSuffix "-" -}}
{{- $ns := default "default" .Values.namespace.name | lower | regexReplaceAll "[^a-z0-9-]" "-" | trunc 30 | trimSuffix "-" -}}
{{- $app := default "app" .Values.application.name | lower | regexReplaceAll "[^a-z0-9-]" "-" | trunc 30 | trimSuffix "-" -}}
{{- $rolebindingName := printf "%s-%s-rolebinding" $env $app | trunc 63 | trimSuffix "-" -}}
{{- $namespace := printf "%s-%s" $env $ns | trunc 63 | trimSuffix "-" -}}
{{- $saName := printf "%s-%s-serviceaccount" $env $app | trunc 63 | trimSuffix "-" -}}
{{- $roleName := printf "%s-%s-role" $env $app | trunc 63 | trimSuffix "-" -}}

apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: {{ $rolebindingName }}
  namespace: {{ $namespace }}
  labels:
    {{- include "charts-library.labels" . | nindent 4 }}

subjects:
  - kind: ServiceAccount
    name: {{ $saName }}
    namespace: {{ $namespace }}

roleRef:
  kind: Role
  name: {{ $roleName }}
  apiGroup: rbac.authorization.k8s.io

{{- end }}
{{- end -}}
