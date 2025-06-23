{{/*
configmapenv

This template defines a Kubernetes ConfigMap for environment variables.
It is rendered only if `.Values.variables` exists and is not empty.
Each key-value pair in `.Values.variables` is added as a separate entry in the ConfigMap.
Usage: {{ include "configmapenv" . }}
*/}}

{{- define "configmapenv" -}}
{{- if and (hasKey .Values "variables") (not (empty .Values.variables )) }}

apiVersion: v1
kind: ConfigMap
metadata:
  # ConfigMap name is dynamically generated from environment and application names.
  name: {{ printf "%s-%s-configmapenv" (.Values.environment.name | lower | replace " " "-") (.Values.application.name | lower | replace " " "-") | quote }}
  namespace: {{ printf "%s-%s" (.Values.environment.name | lower | replace " " "-") (.Values.namespace.name | lower | replace " " "-") | quote }}
  labels:
    {{- include "labels" . | nindent 4 }}
    app.kubernetes.io/name: {{ printf "%s-%s-configmapenv" (.Values.environment.name | lower | replace " " "-") (.Values.application.name | lower | replace " " "-") | quote }}

data:
  # Each variable defined in .Values.variables is added as a key-value pair.
  {{- range $key, $value := .Values.variables }}
  {{ $key }}: {{ $value | quote }}
  {{- end }}

{{- end }}
{{- end -}}
