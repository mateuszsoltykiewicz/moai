{{/*
charts-library.rollout

Argo Rollouts resource for advanced deployment strategies (e.g., canary, blue-green).
Only rendered if .Values.rollout.enabled is true.
Usage: {{ include "charts-library.rollout" . }}
*/}}

{{- define "charts-library.rollout" -}}
{{- if .Values.rollout.enabled }}

{{- $env := default "default" .Values.environment.name | lower | regexReplaceAll "[^a-z0-9-]" "-" | trunc 20 | trimSuffix "-" -}}
{{- $ns := default "default" .Values.namespace.name | lower | regexReplaceAll "[^a-z0-9-]" "-" | trunc 30 | trimSuffix "-" -}}
{{- $app := default "app" .Values.application.name | lower | regexReplaceAll "[^a-z0-9-]" "-" | trunc 30 | trimSuffix "-" -}}
{{- $rolloutName := printf "%s-%s-rollout" $env $app | trunc 63 | trimSuffix "-" -}}
{{- $namespace := printf "%s-%s" $env $ns | trunc 63 | trimSuffix "-" -}}
{{- $containerName := $app }}

apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: {{ $rolloutName }}
  namespace: {{ $namespace }}
  labels:
    {{- include "charts-library.labels" . | nindent 4 }}

spec:
  replicas: {{ .Values.replicaCount | default 1 }}
  selector:
    matchLabels:
      app.kubernetes.io/name: {{ $app }}
      app.kubernetes.io/instance: {{ .Release.Name | lower | regexReplaceAll "[^a-z0-9.-]" "-" | trunc 63 | trimSuffix "-" }}
  template:
    metadata:
      labels:
        {{- include "charts-library.labels" . | nindent 8 }}
    spec:
      containers:
        - name: {{ $containerName }}
          image: "{{ .Values.image.repository }}:{{ .Values.image.tag }}"
          {{- if .Values.containerPort }}
          ports:
            - containerPort: {{ .Values.containerPort }}
          {{- end }}
  strategy:
    {{- if .Values.rollout.strategy }}
    {{- toYaml .Values.rollout.strategy | nindent 4 }}
    {{- else }}
    canary:
      steps:
        - setWeight: 50
        - pause: { duration: 10 }
    {{- end }}

{{- end }}
{{- end -}}
