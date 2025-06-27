{{/*
service

This template defines a Kubernetes Service for the application.

- Supports both Deployment and StatefulSet types.
- Uses dynamic naming conventions based on environment, namespace, and application name.
- All values must be set explicitly in values.yaml; no defaults are used.
- Standard labels are included via the "labels" helper template.

Usage: {{ include "service" . }}
*/}}

{{- define "service" -}}
{{- if .Values.service.enable }}

{{- $env := .Values.environment.name | lower | replace " " "-" }}
{{- $ns := .Values.namespace.name | lower | replace " " "-" }}
{{- $app := .Values.application.name | lower | replace " " "-" }}

{{- if eq .Values.application.type "deployment" }}

apiVersion: v1
kind: Service
metadata:
  name: {{ printf "%s-%s-service" $env $app | quote }}
  namespace: {{ printf "%s-%s" $env $ns | quote }}
  labels:
    {{- include "labels" . | nindent 4 }}
    kubernetes.io/service-name: {{ printf "%s-%s-service" $env $app | quote }}
    app.kubernetes.io/name: {{ printf "%s-%s-service" $env $app | quote }}
  {{- with .Values.service.annotations }}
  annotations:
    {{- toYaml . | nindent 4 }}
  {{- end }}

spec:
  selector:
    app.kubernetes.io/name: {{ printf "%s-%s-deployment" $env $app | quote }}
    namespace: {{ printf "%s-%s" $env $ns | quote }}
    environment: {{ $env | quote }}
  ports:
    - name: {{ printf "%s-%s-port" $env $app | quote }}
      protocol: TCP
      port: {{ .Values.application.container.port.containerPort }}
      targetPort: {{ .Values.application.container.port.containerPort }}
      {{- if contains "websocket" (lower .Values.application.name) }}
      appProtocol: ws
      {{- end }}
  ipFamilies:
    - IPv4
  ipFamilyPolicy: SingleStack

{{- else if eq .Values.application.type "statefulset" }}

apiVersion: v1
kind: Service
metadata:
  name: {{ printf "%s-%s-service" $env $app | quote }}
  namespace: {{ printf "%s-%s" $env $ns | quote }}
  labels:
    {{- include "labels" . | nindent 4 }}
    app.kubernetes.io/name: {{ printf "%s-%s-service" $env $app | quote }}
  {{- with .Values.service.annotations }}
  annotations:
    {{- toYaml . | nindent 4 }}
  {{- end }}

spec:
  ports:
    - name: {{ printf "%s-%s-port" $env $app | quote }}
      port: {{ .Values.application.container.port.containerPort }}
  clusterIP: None
  selector:
    app.kubernetes.io/name: {{ printf "%s-%s-statefulset" $env $app | quote }}
    namespace: {{ printf "%s-%s" $env $ns | quote }}
    environment: {{ $env | quote }}

{{- end }}

{{- end }}
{{- end -}}
