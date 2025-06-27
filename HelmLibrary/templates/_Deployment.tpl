{{/*
deployment

This template defines a Kubernetes Deployment for the application.
It is rendered only if `.Values.application.type` is "deployment".
Supports dynamic configuration of image, environment variables, volumes, ports, probes, and service accounts.
Usage: {{ include "deployment" . }}
*/}}

{{- define "deployment" -}}
{{- if eq (title .Values.application.type) "deployment" }}

apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ printf "%s-%s-deployment" (.Values.environment.name | lower | replace " " "-") (.Values.application.name | lower | replace " " "-") | quote }}
  namespace: {{ printf "%s-%s" (.Values.environment.name | lower | replace " " "-") (.Values.namespace.name | lower | replace " " "-") | quote }}
  labels:
    {{- include "labels" $ | nindent 4 }}
    app.kubernetes.io/name: {{ printf "%s-%s-deployment" (.Values.environment.name | lower | replace " " "-") (.Values.application.name | lower | replace " " "-") | quote }}

spec:
  replicas: {{ .Values.replicaCount }}
  selector:
    matchLabels:
      app.kubernetes.io/name: {{ printf "%s-%s-deployment" (.Values.environment.name | lower | replace " " "-") (.Values.application.name | lower | replace " " "-") | quote }}
      namespace: {{ printf "%s-%s" (.Values.environment.name | lower | replace " " "-") (.Values.namespace.name | lower | replace " " "-") | quote }}
      environment: {{ .Values.environment.name | lower }}
  template:
    metadata:
      labels:
        {{- include "labels" . | nindent 8 }}
        app.kubernetes.io/name: {{ printf "%s-%s-deployment" (.Values.environment.name | lower | replace " " "-") (.Values.application.name | lower | replace " " "-") | quote }}
    spec:
      containers:
        - name: {{ printf "%s-%s-container" (.Values.environment.name | lower | replace " " "-") (.Values.application.name | lower | replace " " "-") | quote }}
          {{- if .Values.image.uri }}
          image: "{{ .Values.image.uri }}:{{ .Values.image.tag }}"
          {{- else }}
          image: "{{ .Values.repository.accountId }}.dkr.ecr.{{ .Values.repository.region }}.amazonaws.com/{{ .Values.environment.name }}/{{ .Values.application.name }}:{{ .Values.image.tag }}"
          {{- end }}

          {{- if and (hasKey .Values "variables") (not (empty .Values.variables)) }}
          envFrom:
            - configMapRef:
                name: {{ printf "%s-%s-configmapenv" (.Values.environment.name | lower | replace " " "-") (.Values.application.name | lower | replace " " "-") | quote }}
          {{- end }}

          {{- if .Values.volumes.enable }}
          volumeMounts:
            {{- if and (hasKey .Values.volumes "list") (not (empty .Values.volumes.list)) }}
            {{- range .Values.volumes.list }}
            - name: {{ .name }}
              mountPath: {{ .mountPath }}
              readOnly: {{ .readOnly }}
            {{- end }}
            {{- end }}
            {{- if and (hasKey .Values "config") (not (empty .Values.config)) }}
            - name: {{ printf "%s-%s-configvolume" (.Values.environment.name | lower | replace " " "-") (.Values.application.name | lower | replace " " "-") | quote }}
              mountPath: {{ .Values.config.mountPath }}
              readOnly: {{ .readOnly }}
            {{- end }}
          {{- end }}

          {{- if .Values.service.enable }}
          ports:
            {{- range .Values.ports }}
            - containerPort: {{ .containerPort }}
              name: {{ printf "%s-%s-port" (.Values.environment.name | lower | replace " " "-") (.Values.application.name | lower | replace " " "-") | quote }}
              protocol: {{ .protocol | upper }}
            {{- end }}
          {{- end }}

          {{- if .Values.resources.enable }}
          resources: {{ include "resources" . | nindent 12 }}
          {{- end }}

          {{- if .Values.livenessProbe.enable }}
          livenessProbe: {{ include "health" . | nindent 12 }}
          {{- end }}

          {{- if .Values.readinessProbe.enable }}
          readinessProbe: {{ include "ready" . | nindent 12 }}
          {{- end }}

          {{- if .Values.serviceAccount.enable }}
          serviceAccountName: {{ printf "%s-%s-serviceaccount" (.Values.environment.name | lower | replace " " "-") (.Values.application.name | lower | replace " " "-") | quote }}
          {{- end }}

      {{- if .Values.volumes.enable }}
      volumes:
        {{- if and (hasKey .Values "config") (not (empty .Values.config)) }}
        - name: {{ printf "%s-%s-configvolume" (.Values.environment.name | lower | replace " " "-") (.Values.application.name | lower | replace " " "-") | quote }}
          configMap:
            name: {{ printf "%s-%s-configmap" (.Values.environment.name | lower | replace " " "-") (.Values.application.name | lower | replace " " "-") | quote }}
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
