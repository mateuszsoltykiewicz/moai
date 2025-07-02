{{/*
charts-library.targetgroupbinding

Defines an AWS Load Balancer Controller TargetGroupBinding resource.
Only rendered if .Values.targetGroup.enable is true.
Usage: {{ include "charts-library.targetgroupbinding" . | nindent }}
*/}}

{{- define "charts-library.targetgroupbinding" -}}
{{- if and (hasKey .Values "targetGroup") (.Values.targetGroup.enable) }}

{{- $env := default "default" .Values.environment.name | lower | regexReplaceAll "[^a-z0-9-]" "-" | trunc 20 | trimSuffix "-" -}}
{{- $ns := default "default" .Values.namespace.name | lower | regexReplaceAll "[^a-z0-9-]" "-" | trunc 30 | trimSuffix "-" -}}
{{- $app := default "app" .Values.application.name | lower | regexReplaceAll "[^a-z0-9-]" "-" | trunc 30 | trimSuffix "-" -}}
{{- $tgbName := printf "%s-%s-targetgroupbinding" $env $app | trunc 63 | trimSuffix "-" -}}
{{- $namespace := printf "%s-%s" $env $ns | trunc 63 | trimSuffix "-" -}}
{{- $svcName := printf "%s-%s-service" $env $app | trunc 63 | trimSuffix "-" -}}
{{- $port := .Values.targetGroup.port | default 80 }}

apiVersion: elbv2.k8s.aws/v1beta1
kind: TargetGroupBinding
metadata:
  name: {{ $tgbName }}
  namespace: {{ $namespace }}
  labels:
    {{- include "charts-library.labels" . | nindent 4 }}

spec:
  serviceRef:
    name: {{ $svcName }}
    port: {{ $port }}
  targetGroupARN: {{ required "targetGroup.arn is required" .Values.targetGroup.arn | quote }}
  {{- if .Values.targetGroup.targetType }}
  targetType: {{ .Values.targetGroup.targetType | quote }}
  {{- end }}
  {{- if .Values.targetGroup.vpcID }}
  vpcID: {{ .Values.targetGroup.vpcID | quote }}
  {{- end }}
  {{- if .Values.targetGroup.nodeSelector }}
  nodeSelector:
    {{- toYaml .Values.targetGroup.nodeSelector | nindent 4 }}
  {{- end }}

{{- end }}
{{- end -}}
