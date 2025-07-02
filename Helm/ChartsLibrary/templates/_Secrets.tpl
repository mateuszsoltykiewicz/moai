{{/*
charts-library.secrets

Renders a list of Kubernetes Secrets for storing sensitive data.
Only rendered if .Values.secrets.enabled is true.
Usage: {{ include "charts-library.secrets" . }}
*/}}

{{- define "charts-library.secrets" -}}
{{- if .Values.secrets.enabled }}

{{- range .Values.secrets.list }}

{{- $env := default "default" $.Values.environment.name | lower | regexReplaceAll "[^a-z0-9-]" "-" | trunc 20 | trimSuffix "-" -}}
{{- $ns := default "default" $.Values.namespace.name | lower | regexReplaceAll "[^a-z0-9-]" "-" | trunc 30 | trimSuffix "-" -}}
{{- $app := default "app" $.Values.application.name | lower | regexReplaceAll "[^a-z0-9-]" "-" | trunc 30 | trimSuffix "-" -}}
{{- $secretName := .name | default "secret" | lower | regexReplaceAll "[^a-z0-9-]" "-" | trunc 30 | trimSuffix "-" -}}
{{- $fullName := printf "%s-%s-%s" $env $app $secretName | trunc 63 | trimSuffix "-" -}}
{{- $namespace := printf "%s-%s" $env $ns | trunc 63 | trimSuffix "-" -}}

apiVersion: v1
kind: Secret
metadata:
  name: {{ $fullName }}
  namespace: {{ $namespace }}
  labels:
    {{- include "charts-library.labels" $ | nindent 4 }}
type: Opaque
data:
  {{- range $key, $value := .data }}
  {{ $key }}: {{ $value | quote }}
  {{- end }}

{{- end }}

{{- end }}
{{- end -}}
