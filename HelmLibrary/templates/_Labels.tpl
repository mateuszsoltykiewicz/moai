{{/*
labels

This helper template defines standard Kubernetes labels for resources.
All values must be explicitly set in values.yaml.
Usage: {{ include "labels" . | nindent }}
*/}}

{{- define "labels" -}}

{{- $appName := .Values.application.name | lower }}
{{- $ownerName := .Values.owner.name | lower }}
{{- $envName := .Values.environment.name | lower }}
{{- $nsName := .Values.namespace.name | lower }}
{{- $component := .Values.component.name | lower }}
{{- $ownerEmail := .Values.owner.email | replace "@" "_" | lower }}

app.kubernetes.io/instance: {{ $appName }}
app.kubernetes.io/part-of: {{ $ownerName }}
app.kubernetes.io/version: {{ .Chart.Version }}
app.kubernetes.io/managed-by: Helm

namespace: "{{ $envName }}-{{ $nsName }}"
environment: {{ $envName }}
app.kubernetes.io/component: {{ $component }}
date: {{ now | htmlDate }}
contact: {{ $ownerEmail }}

{{- end -}}
