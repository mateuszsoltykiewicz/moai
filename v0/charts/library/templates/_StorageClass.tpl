{{/*
storageclass

This template defines a Kubernetes StorageClass for persistent storage used by StatefulSets.

- Rendered only if the application type is "statefulset" and storageClass is enabled.
- Uses AWS EBS CSI driver (ebs.csi.aws.com) as the provisioner.
- All required values must be set explicitly in values.yaml; no defaults are used.
- Naming follows the pattern: <environment>-<application>-storageclass.
- Standard labels are included via the "labels" helper template.
- The StorageClass is marked as non-default for the cluster.

Usage: {{ include "storageclass" . | nindent }}
*/}}

{{- define "storageclass" -}}
{{- if and (eq (lower .Values.application.type) "statefulset") (.Values.storageClass.enable) }}

apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  # StorageClass name dynamically generated from environment and application names.
  name: {{ printf "%s-%s-storageclass" (.Values.environment.name | lower | replace " " "-") (.Values.application.name | lower | replace " " "-") | quote }}
  annotations:
    # This StorageClass is not the default for the cluster.
    storageclass.kubernetes.io/is-default-class: "false"
  labels:
    {{- include "labels" . | nindent 4 }}
    app.kubernetes.io/name: {{ printf "%s-%s-storageclass" (.Values.environment.name | lower | replace " " "-") (.Values.application.name | lower | replace " " "-") | quote }}

provisioner: ebs.csi.aws.com

reclaimPolicy: Retain

allowVolumeExpansion: true

mountOptions:
  - discard

volumeBindingMode: WaitForFirstConsumer

parameters:
  guaranteedReadWriteLatency: "true"

{{- end }}
{{- end -}}
