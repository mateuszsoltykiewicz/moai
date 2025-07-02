{{/*
charts-library.servicemonitor

Defines a Prometheus ServiceMonitor for metrics scraping.
*/}}

{{- define "charts-library.servicemonitor" -}}
{{- if .Values.monitoring.enabled }}

apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: {{ include "charts-library.serviceName" . }}
  namespace: {{ include "charts-library.namespace" . }}
  labels:
    {{- include "charts-library.labels" . | nindent 4 }}
spec:
  selector:
    matchLabels:
      app.kubernetes.io/name: {{ .Values.application.name | lower | regexReplaceAll "[^a-z0-9-]" "-" }}
  endpoints:
    - port: metrics
      path: /metrics
      interval: 30s

{{- end }}
{{- end -}}
