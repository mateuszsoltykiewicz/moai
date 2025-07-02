{{/*
charts-library.ingress

Defines a Kubernetes Ingress resource for the application.
No AWS ALB annotations. NGINX or Traefik annotations supported.
Usage: {{ include "charts-library.ingress" . }}
*/}}

{{- define "charts-library.ingress" -}}
{{- if .Values.ingress.enable }}

{{- $name := include "charts-library.ingressName" . -}}
{{- $namespace := include "charts-library.namespace" . -}}
{{- $svcName := include "charts-library.serviceName" . -}}
{{- $port := .Values.ingress.port | default 8000 -}}
{{- $host := .Values.ingress.host | default (printf "%s.local" .Values.application.name | lower | regexReplaceAll "[^a-z0-9-.]" "-") -}}

apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: {{ $name }}
  namespace: {{ $namespace }}
  labels:
    {{- include "charts-library.labels" . | nindent 4 }}
  {{- with .Values.ingress.annotations }}
  annotations:
    {{- toYaml . | nindent 4 }}
  {{- end }}

spec:
  {{- if .Values.ingress.className }}
  ingressClassName: {{ .Values.ingress.className | quote }}
  {{- end }}
  rules:
    - host: {{ $host | quote }}
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: {{ $svcName }}
                port:
                  number: {{ $port }}

{{- end }}
{{- end -}}
