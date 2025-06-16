{{/*
health

This helper template defines a liveness probe for a Kubernetes container.
It supports both HTTP GET and exec command probes, based on values.
Rendered only if `.Values.livenessProbe.enable` is true.
Usage: {{ include "health" . | nindent }}
*/}}

{{- define "health" -}}
{{- if .Values.livenessProbe.enable }}

{{- /* HTTP GET probe if enabled and no exec command specified */}}
{{- if and .Values.livenessProbe.http (not .Values.livenessProbe.cmd) -}}
httpGet:
  path: {{ .Values.livenessProbe.path | lower }}
  port: {{ .Values.livenessProbe.port }}
  scheme: HTTP

{{- /* Exec probe if enabled and no HTTP GET specified */}}
{{- else if and (not .Values.livenessProbe.http) .Values.livenessProbe.cmd -}}
exec:
  command:
    - 'echo "df"'
{{- end }}

failureThreshold: {{ .Values.livenessProbe.failureThreshold }}
initialDelaySeconds: {{ .Values.livenessProbe.initialDelaySeconds }}
periodSeconds: {{ .Values.livenessProbe.periodSeconds }}
successThreshold: {{ .Values.livenessProbe.successThreshold }}
timeoutSeconds: {{ .Values.livenessProbe.timeoutSeconds }}

{{- end }}
{{- end -}}
