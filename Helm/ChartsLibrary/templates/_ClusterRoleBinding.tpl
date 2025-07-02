{{/*
  clusterrolebinding

  Defines a Kubernetes ClusterRoleBinding for the application.
  - Name: DNS-1123 compliant, max 63 chars, lowercase, hyphens only.
  - Binds the generated ClusterRole to a specified group.
  - Usage: {{ include "charts-library.clusterrolebinding" . }}
*/}}

{{- define "charts-library.clusterrolebinding" -}}
{{- if and .Values.clusterRole.enable .Values.clusterRole.groupName }}

apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: {{ include "charts-library.clusterrolebindingName" . }}
  labels:
    {{- include "charts-library.labels" . | nindent 4 }}
subjects:
  - kind: Group
    name: {{ .Values.clusterRole.groupName | quote }}
    apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: ClusterRole
  name: {{ include "charts-library.clusterroleName" . }}
  apiGroup: rbac.authorization.k8s.io

{{- end }}
{{- end -}}

{{/*
Helper for DNS-1123-compliant ClusterRoleBinding name.
*/}}
{{- define "charts-library.clusterrolebindingName" -}}
{{- $env := default "default" .Values.environment.name | lower | regexReplaceAll "[^a-z0-9-]" "-" | trunc 20 | trimSuffix "-" -}}
{{- $app := default "app" .Values.application.name | lower | regexReplaceAll "[^a-z0-9-]" "-" | trunc 30 | trimSuffix "-" -}}
{{- printf "%s-%s-clusterrolebinding" $env $app | trunc 63 | trimSuffix "-" -}}
{{- end }}
