{{/*
configmap

This template defines a Kubernetes ConfigMap for the application.
It is rendered only if `.Values.config` exists and is not empty.
The ConfigMap loads configuration files as key-value pairs.
Usage: {{ include "configmap" . }}
*/}}

{{- define "configmap" -}}
{{- if and (hasKey .Values "config") (not (empty .Values.config)) }}

apiVersion: v1
kind: ConfigMap
metadata:
  # ConfigMap name is dynamically generated from the environment and application names.
  name: {{ printf "%s-%s-configmap" (.Values.environment.name | lower | replace " " "-") (.Values.application.name | lower | replace " " "-") | quote }}
  namespace: {{ printf "%s-%s" (.Values.environment.name | lower | replace " " "-") (.Values.namespace.name | lower | replace " " "-") | quote }}
  labels:
    {{- include "labels" . | nindent 4 }}
    app.kubernetes.io/name: {{ printf "%s-%s-configmap" (.Values.environment.name | lower | replace " " "-") (.Values.application.name | lower | replace " " "-") | quote }}

data:
  {{ (.Files.Glob .Values.config ).AsConfig | nindent 2 }}

{{- end }}
{{- end -}}
