{{/*
namespace

Namespace resource for isolating application resources.
Only rendered if .Values.namespace.create is true.
*/}}

{{- define "namespace" -}}
{{- if .Values.namespace.create }}

apiVersion: v1
kind: Namespace
metadata:
  # Namespace name is generated from environment and namespace.name.
  name: "{{ .Values.environment.name | lower }}-{{ .Values.namespace.name | lower }}"
  labels:
    # Standard labels included from the "labels" helper template.
    {{- include "labels" . | nindent 4 }}

{{- end }}
{{- end -}}
