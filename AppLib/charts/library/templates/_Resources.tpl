{{/*
resources

This helper template defines the resource requests and limits for a Kubernetes container.

It is rendered only if `.Values.resources.enable` is true.

All resource values must be set explicitly in values.yaml.

Usage: {{ include "resources" . | nindent }}
*/}}

{{- define "resources" -}}
{{- if .Values.resources.enable }}

limits:
  # Maximum amount of CPU the container can use.
  cpu: {{ .Values.resources.limits.cpu | quote }}
  # Maximum amount of memory the container can use.
  memory: {{ .Values.resources.limits.memory | quote }}

requests:
  # Minimum amount of CPU requested for scheduling.
  cpu: {{ .Values.resources.requests.cpu | quote }}
  # Minimum amount of memory requested for scheduling.
  memory: {{ .Values.resources.requests.memory | quote }}

{{- end }}
{{- end -}}
