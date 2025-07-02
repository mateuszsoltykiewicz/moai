{{/*
charts-library.resources

Defines the resource requests and limits for a Kubernetes container.
Renders only if .Values.resources.enable is true.
Usage: {{ include "charts-library.resources" . | nindent }}
*/}}

{{- define "charts-library.resources" -}}
{{- if .Values.resources.enable }}
{{- if or .Values.resources.limits .Values.resources.requests }}
{{- if .Values.resources.limits }}
limits:
  {{- if .Values.resources.limits.cpu }}
  cpu: {{ .Values.resources.limits.cpu | quote }}
  {{- end }}
  {{- if .Values.resources.limits.memory }}
  memory: {{ .Values.resources.limits.memory | quote }}
  {{- end }}
{{- end }}
{{- if .Values.resources.requests }}
requests:
  {{- if .Values.resources.requests.cpu }}
  cpu: {{ .Values.resources.requests.cpu | quote }}
  {{- end }}
  {{- if .Values.resources.requests.memory }}
  memory: {{ .Values.resources.requests.memory | quote }}
  {{- end }}
{{- end }}
{{- end }}
{{- end }}
{{- end -}}
