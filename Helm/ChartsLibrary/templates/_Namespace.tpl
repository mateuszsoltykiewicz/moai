{{/*
charts-library.namespace

Namespace resource for isolating application resources.
Only rendered if .Values.namespace.create is true.
Usage: {{ include "charts-library.namespace" . }}
*/}}

{{- define "charts-library.namespace" -}}
{{- if .Values.namespace.create }}

{{- $env := default "default" .Values.environment.name | lower | regexReplaceAll "[^a-z0-9-]" "-" | trunc 20 | trimSuffix "-" -}}
{{- $ns := default "default" .Values.namespace.name | lower | regexReplaceAll "[^a-z0-9-]" "-" | trunc 30 | trimSuffix "-" -}}
{{- $name := printf "%s-%s" $env $ns | trunc 63 | trimSuffix "-" -}}

apiVersion: v1
kind: Namespace
metadata:
  name: {{ $name }}
  labels:
    {{- include "charts-library.labels" . | nindent 4 }}

{{- end }}
{{- end -}}
