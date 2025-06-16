{{/*
secrets

Renders a list of Kubernetes Secrets for storing sensitive data.

Only rendered if .Values.secrets.enabled is true.

Usage: {{ include "secrets" . }}
*/}}

{{- define "secrets" -}}
{{- if .Values.secrets.enabled }}

{{- range .Values.secrets.list }}

apiVersion: v1
kind: Secret
metadata:
  # Secret name as defined in values.yaml, using naming convention.
  name: {{ printf "%s-%s-%s" 
    ($.Values.environment.name | lower | replace " " "-")
    ($.Values.application.name | lower | replace " " "-")
    (.name | lower | replace " " "-")
    | quote }}
  # Namespace for the Secret, built from environment and namespace names.
  namespace: {{ printf "%s-%s" 
    ($.Values.environment.name | lower | replace " " "-")
    ($.Values.namespace.name | lower | replace " " "-")
    | quote }}
  labels:
    # Standard labels included from the "labels" helper template.
    {{- include "labels" $ | nindent 4 }}
type: Opaque
data:
  {{- range $key, $value := .data }}
  {{ $key }}: {{ $value | quote }}
  {{- end }}

{{- end }}

{{- end }}
{{- end -}}
