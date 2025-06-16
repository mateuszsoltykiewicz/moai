{{/*
poddistruptionbudget

This template defines a Kubernetes PodDisruptionBudget (PDB) to ensure a minimum number of pods are always available for your application.

- Rendered only if `.Values.podDisruptionBudget.enabled` is true.
- The PDB name, namespace, and selectors are built from explicit values in values.yaml.
- Supports both `minAvailable` and `maxUnavailable` (only one should be set).
- Standard labels are included via the "labels" helper template.

Usage: {{ include "poddistruptionbudget" . }}
*/}}

{{- define "poddistruptionbudget" -}}
{{- if .Values.podDisruptionBudget.enabled }}

apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: {{ printf "%s-%s-pdb" (.Values.environment.name | lower | replace " " "-") (.Values.application.name | lower | replace " " "-") | quote }}
  namespace: {{ printf "%s-%s" (.Values.environment.name | lower | replace " " "-") (.Values.namespace.name | lower | replace " " "-") | quote }}
  labels:
    {{- include "labels" . | nindent 4 }}

spec:
  {{- if hasKey .Values.podDisruptionBudget "minAvailable" }}
  minAvailable: {{ .Values.podDisruptionBudget.minAvailable }}
  {{- else if hasKey .Values.podDisruptionBudget "maxUnavailable" }}
  maxUnavailable: {{ .Values.podDisruptionBudget.maxUnavailable }}
  {{- end }}
  selector:
    matchLabels:
      app.kubernetes.io/name: {{ printf "%s-%s-deployment" (.Values.environment.name | lower | replace " " "-") (.Values.application.name | lower | replace " " "-") | quote }}
      namespace: {{ printf "%s-%s" (.Values.environment.name | lower | replace " " "-") (.Values.namespace.name | lower | replace " " "-") | quote }}
      environment: {{ .Values.environment.name | lower | quote }}

{{- end }}
{{- end -}}
