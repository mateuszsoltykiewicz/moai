{{/*
charts-library.networkpolicy

Defines a Kubernetes NetworkPolicy for restricting ingress/egress.
Usage: {{ include "charts-library.networkpolicy" . | nindent }}
*/}}

{{- define "charts-library.networkpolicy" -}}
{{- if .Values.networkPolicy.enabled }}

apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: {{ include "charts-library.networkpolicyName" . }}
  namespace: {{ include "charts-library.namespace" . }}
  labels:
    {{- include "charts-library.labels" . | nindent 4 }}
spec:
  podSelector:
    {{- toYaml .Values.networkPolicy.podSelector | nindent 4 }}
  policyTypes:
    {{- range .Values.networkPolicy.policyTypes }}
    - {{ . | quote }}
    {{- end }}
  {{- if .Values.networkPolicy.ingress }}
  ingress:
    {{- range .Values.networkPolicy.ingress }}
    - {{- if .from }}
        from:
          {{- range .from }}
          - {{ toYaml . | nindent 12 }}
          {{- end }}
      {{- end }}
      {{- if .ports }}
        ports:
          {{- range .ports }}
          - {{ toYaml . | nindent 12 }}
          {{- end }}
      {{- end }}
    {{- end }}
  {{- end }}
  {{- if .Values.networkPolicy.egress }}
  egress:
    {{- range .Values.networkPolicy.egress }}
    - {{- if .to }}
        to:
          {{- range .to }}
          - {{ toYaml . | nindent 12 }}
          {{- end }}
      {{- end }}
      {{- if .ports }}
        ports:
          {{- range .ports }}
          - {{ toYaml . | nindent 12 }}
          {{- end }}
      {{- end }}
    {{- end }}
  {{- end }}

{{- end }}
{{- end -}}
