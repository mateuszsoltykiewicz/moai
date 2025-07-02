{{/*
configmapenv

Defines a Kubernetes ConfigMap for environment variables.
- Name: DNS-1123 compliant, max 63 chars.
- Renders only if .Values.variables is a non-empty map.
- Each key-value pair in .Values.variables is added as a ConfigMap entry.
- Usage: {{ include "charts-library.configmapenv" . }}
*/}}

{{- define "charts-library.configmapenv" -}}
{{- if and (hasKey .Values "variables") (not (empty .Values.variables)) }}

{{- $name := include "charts-library.configmapenvName" . -}}
{{- $namespace := include "charts-library.namespace" . -}}

apiVersion: v1
kind: ConfigMap
metadata:
  name: {{ $name }}
  namespace: {{ $namespace }}
  labels:
    {{- include "charts-library.labels" . | nindent 4 }}

data:
  {{- range $key, $value := .Values.variables }}
  {{ $key | quote }}: {{ $value | quote }}
  {{- end }}

{{- end }}
{{- end -}}

{{/*
Helper for DNS-1123-compliant ConfigMapEnv name.
*/}}
{{- define "charts-library.configmapenvName" -}}
{{- $env := default "default" .Values.environment.name | lower | regexReplaceAll "[^a-z0-9-]" "-" | trunc 20 | trimSuffix "-" -}}
{{- $app := default "app" .Values.application.name | lower | regexReplaceAll "[^a-z0-9-]" "-" | trunc 30 | trimSuffix "-" -}}
{{- printf "%s-%s-configmapenv" $env $app | trunc 63 | trimSuffix "-" -}}
{{- end }}
