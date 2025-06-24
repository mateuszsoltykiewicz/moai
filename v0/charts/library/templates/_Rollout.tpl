{{/*
rollout

Argo Rollouts resource for advanced deployment strategies (e.g., canary, blue-green).

- Only rendered if .Values.rollout.enabled is true.
- All values must be set explicitly in values.yaml; no defaults are used.
- Naming follows the pattern: <environment>-<application>-rollout.
- Namespace follows the pattern: <environment>-<namespace>.
- Standard labels are included for consistency.

Usage: {{ include "rollout" . }}
*/}}

{{- define "rollout" -}}
{{- if .Values.rollout.enabled }}

apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: {{ printf "%s-%s-rollout" (.Values.environment.name | lower | replace " " "-") (.Values.application.name | lower | replace " " "-") | quote }}
  namespace: {{ printf "%s-%s" (.Values.environment.name | lower | replace " " "-") (.Values.namespace.name | lower | replace " " "-") | quote }}
  labels:
    app.kubernetes.io/name: {{ .Values.application.name | lower | replace " " "-" | quote }}
    app.kubernetes.io/instance: {{ .Values.application.name | lower | replace " " "-" | quote }}
    app.kubernetes.io/managed-by: Helm

spec:
  replicas: {{ .Values.replicaCount }}
  selector:
    matchLabels:
      app.kubernetes.io/name: {{ .Values.application.name | lower | replace " " "-" | quote }}
      app.kubernetes.io/instance: {{ .Values.application.name | lower | replace " " "-" | quote }}
  template:
    metadata:
      labels:
        app.kubernetes.io/name: {{ .Values.application.name | lower | replace " " "-" | quote }}
        app.kubernetes.io/instance: {{ .Values.application.name | lower | replace " " "-" | quote }}
    spec:
      containers:
        - name: {{ .Values.application.name | lower | replace " " "-" | quote }}
          image: "{{ .Values.image.repository }}:{{ .Values.image.tag }}"
          ports:
            - containerPort: {{ .Values.containerPort }}
  strategy:
    canary:
      steps:
        - setWeight: 50
        - pause: { duration: 10 }

{{- end }}
{{- end -}}
