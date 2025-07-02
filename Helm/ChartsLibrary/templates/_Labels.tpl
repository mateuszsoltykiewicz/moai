{{/*
charts-library.labels

Defines standard Kubernetes labels for resources.
- All values are sanitized and truncated for compliance.
- Only stable values are used as labels; others should be annotations.
- Usage: {{ include "charts-library.labels" . | nindent }}
*/}}

{{- define "charts-library.labels" -}}
{{- $appName := default "app" .Values.application.name | lower | regexReplaceAll "[^a-z0-9.-]" "-" | trunc 63 | trimSuffix "-" -}}
{{- $owner := default "team" .Values.owner.name | lower | regexReplaceAll "[^a-z0-9.-]" "-" | trunc 63 | trimSuffix "-" -}}
{{- $env := default "default" .Values.environment.name | lower | regexReplaceAll "[^a-z0-9.-]" "-" | trunc 63 | trimSuffix "-" -}}
{{- $ns := default "default" .Values.namespace.name | lower | regexReplaceAll "[^a-z0-9.-]" "-" | trunc 63 | trimSuffix "-" -}}
{{- $component := default "main" .Values.component.name | lower | regexReplaceAll "[^a-z0-9.-]" "-" | trunc 63 | trimSuffix "-" -}}

app.kubernetes.io/name: {{ $appName }}
app.kubernetes.io/instance: {{ .Release.Name | lower | regexReplaceAll "[^a-z0-9.-]" "-" | trunc 63 | trimSuffix "-" }}
app.kubernetes.io/part-of: {{ .Chart.Name | lower | regexReplaceAll "[^a-z0-9.-]" "-" | trunc 63 | trimSuffix "-" }}
app.kubernetes.io/version: {{ .Chart.Version | quote }}
app.kubernetes.io/managed-by: {{ .Release.Service | quote }}
app.kubernetes.io/component: {{ $component }}
environment: {{ $env }}
namespace: {{ $ns }}
owner: {{ $owner }}
{{- end }}
