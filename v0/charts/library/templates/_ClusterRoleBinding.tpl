{{/*
  clusterrolebinding

  This template defines a Kubernetes ClusterRoleBinding for the application.
  It binds the generated ClusterRole to a specified group (must be set in values).
  Rendering is conditional on `.Values.clusterRole.enable`.
  Usage: {{ include "clusterrolebinding" . }}
*/}}
{{- define "clusterrolebinding" -}}
{{- if .Values.clusterRole.enable }}

apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  # The ClusterRoleBinding name is dynamically generated from environment and application names.
  name: {{ printf "%s-%s-clusterrolebinding" (.Values.environment.name | lower | replace " " "-") (.Values.application.name | lower | replace " " "-") | quote }}
  labels:
    {{- include "labels" . | nindent 4 }}
subjects:
  - kind: Group
    name: {{ .Values.clusterRole.groupName | quote }}
    apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: ClusterRole
  name: {{ printf "%s-%s-clusterrole" (.Values.environment.name | lower | replace " " "-") (.Values.application.name | lower | replace " " "-") | quote }}
  apiGroup: rbac.authorization.k8s.io

{{- end }}
{{- end -}}
