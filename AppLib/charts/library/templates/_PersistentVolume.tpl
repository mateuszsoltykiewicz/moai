{{/*
persistentvolume

This template defines a Kubernetes PersistentVolume (PV) for stateful applications.

- It is rendered only if `.Values.application.type` is "statefulset".
- The PV name and storageClassName are dynamically generated from environment and application names, ensuring uniqueness and consistency.
- All required values (environment, application, volume size, access mode, host path) must be set explicitly in values.yaml.
- The reclaim policy is set to "Retain" to ensure data is not deleted if the PVC is removed, following Kubernetes best practices for stateful workloads.
- Standard labels are included via the "labels" helper template.

Usage: {{ include "persistentvolume" . }}

*/}}

{{- define "persistentvolume" -}}
{{- if eq .Values.application.type "statefulset" }}

apiVersion: v1
kind: PersistentVolume
metadata:
  # PersistentVolume name is dynamically generated from environment and application names.
  name: {{ printf "%s-%s-pv" (.Values.environment.name | lower | replace " " "-") (.Values.application.name | lower | replace " " "-") | quote }}
  labels:
    # Standard labels included from the "labels" helper template.
    {{- include "labels" . | nindent 4 }}

spec:
  capacity:
    # The requested storage size for the PV.
    storage: {{ .Values.volume.size }}
  accessModes:
    # The access mode for the PV (e.g., ReadWriteOnce).
    - {{ .Values.volume.accessMode }}
  # Retain policy ensures the PV is not deleted automatically when released.
  persistentVolumeReclaimPolicy: Retain
  # Storage class name is dynamically generated from environment and application names.
  storageClassName: {{ printf "%s-%s-storageclass" (.Values.environment.name | lower | replace " " "-") (.Values.application.name | lower | replace " " "-") | quote }}
  hostPath:
    # Host path on the node where the volume is stored.
    path: {{ .Values.volume.hostPath }}

{{- end }}
{{- end -}}
