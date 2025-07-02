{{/*
horizontalpodautoscaling

HorizontalPodAutoscaler for scaling pods based on resource utilization or custom metrics.
Only rendered if .Values.hpa.enabled is true.
Usage: {{ include "charts-library.horizontalpodautoscaling" . }}
*/}}

{{- define "charts-library.horizontalpodautoscaling" -}}
{{- if .Values.hpa.enabled }}

{{- $env := default "default" .Values.environment.name | lower | regexReplaceAll "[^a-z0-9-]" "-" | trunc 20 | trimSuffix "-" -}}
{{- $ns := default "default" .Values.namespace.name | lower | regexReplaceAll "[^a-z0-9-]" "-" | trunc 30 | trimSuffix "-" -}}
{{- $app := default "app" .Values.application.name | lower | regexReplaceAll "[^a-z0-9-]" "-" | trunc 30 | trimSuffix "-" -}}

{{- $kind := (eq (lower .Values.application.type) "statefulset" | ternary "StatefulSet" "Deployment") -}}
{{- $targetName := (eq $kind "Deployment" | ternary (include "charts-library.deploymentName" .) (include "charts-library.statefulsetName" .)) }}

apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: {{ printf "%s-%s-hpa" $env $app | trunc 63 | trimSuffix "-" }}
  namespace: {{ printf "%s-%s" $env $ns | trunc 63 | trimSuffix "-" }}
  labels:
    {{- include "charts-library.labels" . | nindent 4 }}

spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: {{ $kind }}
    name: {{ $targetName }}

  minReplicas: {{ .Values.hpa.minReplicas | default 1 }}
  maxReplicas: {{ .Values.hpa.maxReplicas | default 10 }}

  metrics:
    {{- if .Values.hpa.metrics }}
    {{- toYaml .Values.hpa.metrics | nindent 4 }}
    {{- else }}
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: {{ .Values.hpa.targetCPUUtilizationPercentage | default 80 }}
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
