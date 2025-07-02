{{/*
charts-library.service

Defines a Kubernetes Service for the application.
- Supports both Deployment and StatefulSet types.
- Usage: {{ include "charts-library.service" . }}
*/}}

{{- define "charts-library.service" -}}
{{- if .Values.service.enable }}

{{- $env := default "default" .Values.environment.name | lower | regexReplaceAll "[^a-z0-9-]" "-" | trunc 20 | trimSuffix "-" -}}
{{- $ns := default "default" .Values.namespace.name | lower | regexReplaceAll "[^a-z0-9-]" "-" | trunc 30 | trimSuffix "-" -}}
{{- $app := default "app" .Values.application.name | lower | regexReplaceAll "[^a-z0-9-]" "-" | trunc 30 | trimSuffix "-" -}}
{{- $svcName := printf "%s-%s-service" $env $app | trunc 63 | trimSuffix "-" -}}
{{- $namespace := printf "%s-%s" $env $ns | trunc 63 | trimSuffix "-" -}}

apiVersion: v1
kind: Service
metadata:
  name: {{ $svcName }}
  namespace: {{ $namespace }}
  labels:
    {{- include "charts-library.labels" . | nindent 4 }}
  {{- with .Values.service.annotations }}
  annotations:
    {{- toYaml . | nindent 4 }}
  {{- end }}

spec:
  {{- if eq (lower .Values.application.type) "statefulset" }}
  clusterIP: None
  {{- end }}
  selector:
    app.kubernetes.io/name: {{ $app }}
    app.kubernetes.io/instance: {{ .Release.Name | lower | regexReplaceAll "[^a-z0-9.-]" "-" | trunc 63 | trimSuffix "-" }}
  ports:
    {{- range .Values.service.ports }}
    - name: {{ .name | default (printf "%s-%s-port" $env $app) | trunc 63 | trimSuffix "-" }}
      port: {{ .port }}
      targetPort: {{ .targetPort | default .port }}
      protocol: {{ .protocol | default "TCP" | upper }}
      {{- if .appProtocol }}
      appProtocol: {{ .appProtocol | quote }}
      {{- end }}
    {{- end }}
  ipFamilies:
    - IPv4
  ipFamilyPolicy: SingleStack

{{- end }}
{{- end -}}
