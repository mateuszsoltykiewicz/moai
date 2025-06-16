{{/*
ready

This helper template defines a readiness probe for a Kubernetes container.

It supports both HTTP GET and exec command probes, based on values.

Rendered only if `.Values.readinessProbe.enable` is true.

Usage: {{ include "ready" . | nindent }}
*/}}

{{- define "ready" -}}
{{- if .Values.readinessProbe.enable }}

{{- /* HTTP GET probe if enabled and no exec command specified */}}
{{- if and .Values.readinessProbe.http (not .Values.readinessProbe.cmd) -}}
httpGet:
  path: {{ .Values.readinessProbe.path }}
  port: {{ .Values.readinessProbe.port }}
  scheme: HTTP

{{- /* Exec probe if enabled and no HTTP GET specified */}}
{{- else if and (not .Values.readinessProbe.http) .Values.readinessProbe.cmd -}}
exec:
  command:
    - 'echo "df"'
{{- end }}

failureThreshold: {{ .Values.readinessProbe.failureThreshold }}
periodSeconds: {{ .Values.readinessProbe.periodSeconds }}
successThreshold: {{ .Values.readinessProbe.successThreshold }}
timeoutSeconds: {{ .Values.readinessProbe.timeoutSeconds }}

{{- end }}
{{- end -}}
