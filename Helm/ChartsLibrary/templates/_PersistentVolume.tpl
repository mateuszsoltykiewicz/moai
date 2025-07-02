{{/*
charts-library.persistentvolume

Defines a Kubernetes PersistentVolume (PV) for stateful applications using hostPath.
Only rendered if .Values.application.type == "statefulset".
Usage: {{ include "charts-library.persistentvolume" . }}
*/}}

{{- define "charts-library.persistentvolume" -}}
{{- if eq (lower .Values.application.type) "statefulset" }}

{{- $env := default "default" .Values.environment.name | lower | regexReplaceAll "[^a-z0-9-]" "-" | trunc 20 | trimSuffix "-" -}}
{{- $app := default "app" .Values.application.name | lower | regexReplaceAll "[^a-z0-9-]" "-" | trunc 30 | trimSuffix "-" -}}
{{- $pvName := printf "%s-%s-pv" $env $app | trunc 63 | trimSuffix "-" -}}
{{- $scName := printf "%s-%s-storageclass" $env $app | trunc 63 | trimSuffix "-" -}}

apiVersion: v1
kind: PersistentVolume
metadata:
  name: {{ $pvName }}
  labels:
    {{- include "charts-library.labels" . | nindent 4 }}

spec:
  capacity:
    storage: {{ required "volume.size is required" .Values.volume.size }}
  accessModes:
    - {{ required "volume.accessMode is required" .Values.volume.accessMode }}
  persistentVolumeReclaimPolicy: Retain
  storageClassName: {{ $scName }}
  hostPath:
    path: {{ required "volume.hostPath is required" .Values.volume.hostPath }}

{{- end }}
{{- end -}}
