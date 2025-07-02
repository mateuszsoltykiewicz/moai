{{/*
charts-library.job

Defines a Kubernetes Job for batch tasks.
Usage: {{ include "charts-library.job" . | nindent }}
*/}}

{{- define "charts-library.job" -}}
{{- if .Values.job.enabled }}

apiVersion: batch/v1
kind: Job
metadata:
  name: {{ include "charts-library.jobName" . }}
  namespace: {{ include "charts-library.namespace" . }}
  labels:
    {{- include "charts-library.labels" . | nindent 4 }}
spec:
  template:
    metadata:
      labels:
        {{- include "charts-library.labels" . | nindent 8 }}
    spec:
      restartPolicy: Never
      {{- include "charts-library.initContainers" . | nindent 6 }}
      containers:
        - name: {{ include "charts-library.jobName" . }}
          image: "{{ .Values.job.image }}"
          command: {{ toYaml .Values.job.command | nindent 10 }}
          envFrom:
            - configMapRef:
                name: {{ include "charts-library.configmapenvName" . }}
{{- end }}
{{- end -}}
