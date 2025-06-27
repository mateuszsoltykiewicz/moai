{{/*
horizontalpodautoscaling

HorizontalPodAutoscaler for scaling pods based on resource utilization or custom metrics.
Only rendered if .Values.hpa.enabled is true.
Usage: {{ include "horizontalpodautoscaling" . }}
*/}}

{{- define "horizontalpodautoscaling" -}}
{{- if .Values.hpa.enabled }}

{{- $env := .Values.environment.name | lower | replace " " "-" }}
{{- $namespace := .Values.namespace.name | lower | replace " " "-" }}
{{- $app := .Values.application.name | lower | replace " " "-" }}

apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: {{ printf "%s-%s-hpa" $env $app | quote }}
  namespace: {{ printf "%s-%s" $env $namespace | quote }}
  labels:
    {{- include "labels" . | nindent 4 }}

spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: {{ .Values.application.type | title }}
    name: {{ printf "%s-%s-deployment" $env $app | quote }}

  minReplicas: {{ .Values.hpa.minReplicas }}
  maxReplicas: {{ .Values.hpa.maxReplicas }}

  metrics:
    {{- if .Values.hpa.metrics }}
    {{- toYaml .Values.hpa.metrics | nindent 4 }}
    {{- else }}
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: {{ .Values.hpa.targetCPUUtilizationPercentage }}
    {{- end }}

  {{- if .Values.hpa.behavior }}
  behavior:
    {{- toYaml .Values.hpa.behavior | nindent 4 }}
  {{- else }}
  behavior:
    scaleUp:
      stabilizationWindowSeconds: 0
      selectPolicy: Max
      policies:
        - type: Percent
          value: 100
          periodSeconds: 60
    scaleDown:
      stabilizationWindowSeconds: 300
      selectPolicy: Min
      policies:
        - type: Pods
          value: 4
          periodSeconds: 60
        - type: Percent
          value: 10
          periodSeconds: 60
  {{- end }}

{{- end }}
{{- end -}}
