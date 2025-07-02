{{/*
charts-library.livenessProbe

Defines a liveness probe for a Kubernetes container.
Supports HTTP GET or exec command, based on values.
Usage: {{ include "charts-library.livenessProbe" . | nindent }}
*/}}

{{- define "charts-library.livenessProbe" -}}
{{- if .Values.livenessProbe.enable }}

{{- if and .Values.livenessProbe.http (not .Values.livenessProbe.cmd) }}
httpGet:
  path: {{ .Values.livenessProbe.path | default "/health/live" | quote }}
  port: {{ .Values.livenessProbe.port | default 8000 }}
  scheme: {{ .Values.livenessProbe.scheme | default "HTTP" | upper }}
{{- else if and (not .Values.livenessProbe.http) .Values.livenessProbe.cmd }}
exec:
  command:
    {{- range .Values.livenessProbe.cmd }}
    - {{ . | quote }}
    {{- end }}
{{- end }}

failureThreshold: {{ .Values.livenessProbe.failureThreshold | default 3 }}
initialDelaySeconds: {{ .Values.livenessProbe.initialDelaySeconds | default 10 }}
periodSeconds: {{ .Values.livenessProbe.periodSeconds | default 10 }}
successThreshold: {{ .Values.livenessProbe.successThreshold | default 1 }}
timeoutSeconds: {{ .Values.livenessProbe.timeoutSeconds | default 1 }}

{{- end }}
{{- end -}}
