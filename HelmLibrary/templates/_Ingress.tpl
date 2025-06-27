{{/*
ingress

This template defines a Kubernetes Ingress resource for the application.
It is rendered only if `.Values.ingress.enable` is true.
Supports dynamic annotations, host, className, and backend service configuration.
Usage: {{ include "ingress" . }}
*/}}

{{- define "ingress" -}}
{{- if .Values.ingress.enable }}

apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: {{ printf "%s-%s-ingress" (.Values.environment.name | lower | replace " " "-") (.Values.application.name | lower | replace " " "-") | quote }}
  namespace: {{ printf "%s-%s" (.Values.environment.name | lower | replace " " "-") (.Values.namespace.name | lower | replace " " "-") | quote }}
  labels:
    {{- include "labels" . | nindent 4 }}
    app.kubernetes.io/name: {{ printf "%s-%s-ingress" (.Values.environment.name | lower | replace " " "-") (.Values.application.name | lower | replace " " "-") | quote }}
  {{- if and (hasKey .Values.ingress "annotations") (not (empty .Values.ingress.annotations)) }}
  annotations:
    {{- range $key, $value := .Values.ingress.annotations }}
    {{ $key }}: {{ $value | quote }}
    {{- end }}
  {{- end }}

spec:
  ingressClassName: {{ .Values.ingress.className | quote }}
  rules:
    {{- if eq (.Values.application.name | title) "Frontend" }}
    - host: {{ .Values.ingress.host | quote }}
    {{- else }}
    - host: {{ printf "%s.%s" (.Values.application.name | lower | replace " " "-") .Values.ingress.host | quote }}
    {{- end }}
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: {{ printf "%s-%s-service" (.Values.environment.name | lower | replace " " "-") (.Values.application.name | lower | replace " " "-") | quote }}
                port:
                  name: {{ printf "%s-%s-port" (.Values.environment.name | lower | replace " " "-") (.Values.application.name | lower | replace " " "-") | quote }}

{{- end }}
{{- end -}}
