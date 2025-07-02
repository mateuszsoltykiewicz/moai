{{/*
charts-library.poddisruptionbudget

Defines a Kubernetes PodDisruptionBudget (PDB).
- Only rendered if .Values.podDisruptionBudget.enabled is true.
- Usage: {{ include "charts-library.poddisruptionbudget" . }}
*/}}

{{- define "charts-library.poddisruptionbudget" -}}
{{- if .Values.podDisruptionBudget.enabled }}

{{- $env := default "default" .Values.environment.name | lower | regexReplaceAll "[^a-z0-9-]" "-" | trunc 20 | trimSuffix "-" -}}
{{- $ns := default "default" .Values.namespace.name | lower | regexReplaceAll "[^a-z0-9-]" "-" | trunc 30 | trimSuffix "-" -}}
{{- $app := default "app" .Values.application.name | lower | regexReplaceAll "[^a-z0-9-]" "-" | trunc 30 | trimSuffix "-" -}}
{{- $pdbName := printf "%s-%s-pdb" $env $app | trunc 63 | trimSuffix "-" -}}

apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: {{ $pdbName }}
  namespace: {{ printf "%s-%s" $env $ns | trunc 63 | trimSuffix "-" }}
  labels:
    {{- include "charts-library.labels" . | nindent 4 }}

spec:
  {{- if hasKey .Values.podDisruptionBudget "minAvailable" }}
  minAvailable: {{ .Values.podDisruptionBudget.minAvailable }}
  {{- else if hasKey .Values.podDisruptionBudget "maxUnavailable" }}
  maxUnavailable: {{ .Values.podDisruptionBudget.maxUnavailable }}
  {{- end }}
  selector:
    matchLabels:
      app.kubernetes.io/name: {{ $app }}
      app.kubernetes.io/instance: {{ .Release.Name | lower | regexReplaceAll "[^a-z0-9.-]" "-" | trunc 63 | trimSuffix "-" }}

{{- end }}
{{- end -}}
