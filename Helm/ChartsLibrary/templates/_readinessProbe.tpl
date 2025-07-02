{{/*
charts-library.readinessProbe

Defines a readiness probe for a Kubernetes container.
Supports HTTP GET or exec command, based on values.
Usage: {{ include "charts-library.readinessProbe" . | nindent }}
*/}}

{{- define "charts-library.readinessProbe" -}}
{{- if .Values.readinessProbe.enable }}

{{- if and .Values.readinessProbe.http (not .Values.readinessProbe.cmd) }}
httpGet:
  path: {{ .Values.readinessProbe.path | default "/health/ready" | quote }}
  port: {{ .Values.readinessProbe.port | default 8000 }}
  scheme: {{ .Values.readinessProbe.scheme | default "HTTP" | upper }}
{{- else if and (not .Values.readinessProbe.http) .Values.readinessProbe.cmd }}
exec:
  command:
    {{- range .Values.readinessProbe.cmd }}
    - {{ . | quote }}
    {{- end }}
{{- end }}

failureThreshold: {{ .Values.readinessProbe.failureThreshold | default 3 }}
initialDelaySeconds: {{ .Values.readinessProbe.initialDelaySeconds | default 10 }}
periodSeconds: {{ .Values.readinessProbe.periodSeconds | default 10 }}
successThreshold: {{ .Values.readinessProbe.successThreshold | default 1 }}
timeoutSeconds: {{ .Values.readinessProbe.timeoutSeconds | default 1 }}

{{- end }}
{{- end -}}
