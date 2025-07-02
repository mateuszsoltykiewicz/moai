{{/*
configmap

Defines a Kubernetes ConfigMap for the application.
- Name: DNS-1123 compliant, max 63 chars.
- Renders only if .Values.configGlob is set and files are found.
- Loads configuration files as key-value pairs.
- Usage: {{ include "charts-library.configmap" . }}
*/}}

{{- define "charts-library.configmap" -}}
{{- if and (hasKey .Values "configGlob") (not (empty .Values.configGlob)) }}

{{- $name := include "charts-library.configmapName" . -}}
{{- $namespace := include "charts-library.namespace" . -}}
{{- $files := .Files.Glob .Values.configGlob -}}
{{- if $files }}

apiVersion: v1
kind: ConfigMap
metadata:
  name: {{ $name }}
  namespace: {{ $namespace }}
  labels:
    {{- include "charts-library.labels" . | nindent 4 }}

data:
{{- $files.AsConfig | nindent 2 }}

{{- end }}
{{- end }}
{{- end -}}

{{/*
Helper for DNS-1123-compliant ConfigMap name.
*/}}
{{- define "charts-library.configmapName" -}}
{{- $env := default "default" .Values.environment.name | lower | regexReplaceAll "[^a-z0-9-]" "-" | trunc 20 | trimSuffix "-" -}}
{{- $app := default "app" .Values.application.name | lower | regexReplaceAll "[^a-z0-9-]" "-" | trunc 30 | trimSuffix "-" -}}
{{- printf "%s-%s-configmap" $env $app | trunc 63 | trimSuffix "-" -}}
{{- end }}

{{/*
Helper for DNS-1123-compliant namespace name.
*/}}
{{- define "charts-library.namespace" -}}
{{- $env := default "default" .Values.environment.name | lower | regexReplaceAll "[^a-z0-9-]" "-" | trunc 20 | trimSuffix "-" -}}
{{- $ns := default "default" .Values.namespace.name | lower | regexReplaceAll "[^a-z0-9-]" "-" | trunc 30 | trimSuffix "-" -}}
{{- printf "%s-%s" $env $ns | trunc 63 | trimSuffix "-" -}}
{{- end }}
