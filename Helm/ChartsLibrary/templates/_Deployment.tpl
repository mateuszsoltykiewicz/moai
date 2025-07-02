{{/*
deployment

Defines a Kubernetes Deployment for the application.
- Name: DNS-1123 compliant, max 63 chars.
- Renders only if .Values.application.type == "deployment".
- Usage: {{ include "charts-library.deployment" . }}
*/}}

{{- define "charts-library.deployment" -}}
{{- if eq (lower .Values.application.type) "deployment" }}

{{- $name := include "charts-library.deploymentName" . -}}
{{- $namespace := include "charts-library.namespace" . -}}

apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ $name }}
  namespace: {{ $namespace }}
  labels:
    {{- include "charts-library.labels" . | nindent 4 }}

spec:
  replicas: {{ default 1 .Values.replicaCount }}
  selector:
    matchLabels:
      app.kubernetes.io/name: {{ $name }}
  template:
    metadata:
      labels:
        {{- include "charts-library.labels" . | nindent 8 }}
    spec:
      {{- include "charts-library.initContainers" . | nindent 6 }}
      containers:
        - name: {{ include "charts-library.containerName" . }}
          image: "{{ .Values.image.uri | default (printf \"%s.dkr.ecr.%s.amazonaws.com/%s/%s:%s\" .Values.repository.accountId .Values.repository.region .Values.environment.name .Values.application.name .Values.image.tag) }}"
          {{- if and (hasKey .Values "variables") (not (empty .Values.variables)) }}
          envFrom:
            - configMapRef:
                name: {{ include "charts-library.configmapenvName" . }}
          {{- end }}
          {{- if .Values.volumes.enable }}
          volumeMounts:
            {{- if and (hasKey .Values.volumes "list") (not (empty .Values.volumes.list)) }}
            {{- range .Values.volumes.list }}
            - name: {{ .name }}
              mountPath: {{ .mountPath }}
              readOnly: {{ .readOnly | default false }}
            {{- end }}
            {{- end }}
            {{- if and (hasKey .Values "config") (not (empty .Values.config)) }}
            - name: {{ include "charts-library.configVolumeName" . }}
              mountPath: {{ .Values.config.mountPath }}
              readOnly: {{ .Values.config.readOnly | default true }}
            {{- end }}
          {{- end }}
          {{- if .Values.service.enable }}
          ports:
            {{- range .Values.ports }}
            - containerPort: {{ .containerPort }}
              name: {{ .name | default (printf "%s-port" $name) }}
              protocol: {{ .protocol | upper | default "TCP" }}
            {{- end }}
          {{- end }}
          {{- if .Values.resources.enable }}
          resources: {{ include "charts-library.resources" . | nindent 12 }}
          {{- end }}
          {{- if .Values.livenessProbe.enable }}
          livenessProbe: {{ include "charts-library.livenessProbe" . | nindent 12 }}
          {{- end }}
          {{- if .Values.readinessProbe.enable }}
          readinessProbe: {{ include "charts-library.readinessProbe" . | nindent 12 }}
          {{- end }}
      {{- if .Values.serviceAccount.enable }}
      serviceAccountName: {{ include "charts-library.serviceAccountName" . }}
      {{- end }}
      {{- if .Values.volumes.enable }}
      volumes:
        {{- if and (hasKey .Values "config") (not (empty .Values.config)) }}
        - name: {{ include "charts-library.configVolumeName" . }}
          configMap:
            name: {{ include "charts-library.configmapName" . }}
        {{- end }}
        {{- if and (hasKey .Values.volumes "list") (not (empty .Values.volumes.list)) }}
        {{- range .Values.volumes.list }}
        - name: {{ .name }}
          emptyDir:
            {{- if .size }}
            sizeLimit: {{ .size }}
            {{- end }}
        {{- end }}
        {{- end }}
      {{- end }}

{{- end }}
{{- end -}}

{{/*
Helper for DNS-1123-compliant Deployment name.
*/}}
{{- define "charts-library.deploymentName" -}}
{{- $env := default "default" .Values.environment.name | lower | regexReplaceAll "[^a-z0-9-]" "-" | trunc 20 | trimSuffix "-" -}}
{{- $app := default "app" .Values.application.name | lower | regexReplaceAll "[^a-z0-9-]" "-" | trunc 30 | trimSuffix "-" -}}
{{- printf "%s-%s-deployment" $env $app | trunc 63 | trimSuffix "-" -}}
{{- end }}

{{/*
Helper for DNS-1123-compliant container name.
*/}}
{{- define "charts-library.containerName" -}}
{{- $env := default "default" .Values.environment.name | lower | regexReplaceAll "[^a-z0-9-]" "-" | trunc 20 | trimSuffix "-" -}}
{{- $app := default "app" .Values.application.name | lower | regexReplaceAll "[^a-z0-9-]" "-" | trunc 30 | trimSuffix "-" -}}
{{- printf "%s-%s-container" $env $app | trunc 63 | trimSuffix "-" -}}
{{- end }}

{{/*
Helper for DNS-1123-compliant config volume name.
*/}}
{{- define "charts-library.configVolumeName" -}}
{{- $env := default "default" .Values.environment.name | lower | regexReplaceAll "[^a-z0-9-]" "-" | trunc 20 | trimSuffix "-" -}}
{{- $app := default "app" .Values.application.name | lower | regexReplaceAll "[^a-z0-9-]" "-" | trunc 30 | trimSuffix "-" -}}
{{- printf "%s-%s-configvolume" $env $app | trunc 63 | trimSuffix "-" -}}
{{- end }}
