{{/*
charts-library.storageclass

Defines a Kubernetes StorageClass for persistent storage using MicroK8s hostpath.
Only rendered if .Values.storageClass.enable is true.
Usage: {{ include "charts-library.storageclass" . | nindent }}
*/}}

{{- define "charts-library.storageclass" -}}
{{- if .Values.storageClass.enable }}

{{- $env := default "default" .Values.environment.name | lower | regexReplaceAll "[^a-z0-9-]" "-" | trunc 20 | trimSuffix "-" -}}
{{- $app := default "app" .Values.application.name | lower | regexReplaceAll "[^a-z0-9-]" "-" | trunc 30 | trimSuffix "-" -}}
{{- $scName := printf "%s-%s-storageclass" $env $app | trunc 63 | trimSuffix "-" -}}

apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: {{ $scName }}
  annotations:
    storageclass.kubernetes.io/is-default-class: "false"
  labels:
    {{- include "charts-library.labels" . | nindent 4 }}

provisioner: {{ .Values.storageClass.provisioner | default "microk8s.io/hostpath" }}

reclaimPolicy: {{ .Values.storageClass.reclaimPolicy | default "Retain" }}

allowVolumeExpansion: {{ .Values.storageClass.allowVolumeExpansion | default true }}

{{- if .Values.storageClass.mountOptions }}
mountOptions:
  {{- toYaml .Values.storageClass.mountOptions | nindent 2 }}
{{- end }}

volumeBindingMode: {{ .Values.storageClass.volumeBindingMode | default "WaitForFirstConsumer" }}

{{- end }}
{{- end -}}
