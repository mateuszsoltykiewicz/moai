{{/*
charts-library.statefulset

Defines a Kubernetes StatefulSet for stateful applications.
Only rendered if .Values.application.type == "statefulset".
Usage: {{ include "charts-library.statefulset" . | nindent }}
*/}}

{{- define "charts-library.statefulset" -}}
{{- if eq (lower .Values.application.type) "statefulset" }}

{{- $env := default "default" .Values.environment.name | lower | regexReplaceAll "[^a-z0-9-]" "-" | trunc 20 | trimSuffix "-" -}}
{{- $ns := default "default" .Values.namespace.name | lower | regexReplaceAll "[^a-z0-9-]" "-" | trunc 30 | trimSuffix "-" -}}
{{- $app := default "app" .Values.application.name | lower | regexReplaceAll "[^a-z0-9-]" "-" | trunc 30 | trimSuffix "-" -}}
{{- $ssName := printf "%s-%s-statefulset" $env $app | trunc 63 | trimSuffix "-" -}}
{{- $namespace := printf "%s-%s" $env $ns | trunc 63 | trimSuffix "-" -}}
{{- $svcName := printf "%s-%s-service" $env $app | trunc 63 | trimSuffix "-" -}}
{{- $containerName := printf "%s-%s-container" $env $app | trunc 63 | trimSuffix "-" -}}
{{- $pvcName := printf "%s-%s-pvc" $env $app | trunc 63 | trimSuffix "-" -}}
{{- $storageClass := printf "%s-%s-storageclass" $env $app | trunc 63 | trimSuffix "-" -}}

apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: {{ $ssName }}
  namespace: {{ $namespace }}
  labels:
    {{- include "charts-library.labels" . | nindent 4 }}

spec:
  selector:
    matchLabels:
      app.kubernetes.io/name: {{ $app }}
      app.kubernetes.io/instance: {{ .Release.Name | lower | regexReplaceAll "[^a-z0-9.-]" "-" | trunc 63 | trimSuffix "-" }}
  serviceName: {{ $svcName }}
  replicas: {{ .Values.replicaCount | default 1 }}
  minReadySeconds: 10

  template:
    metadata:
      labels:
        {{- include "charts-library.labels" . | nindent 8 }}
    spec:
      terminationGracePeriodSeconds: 10
      {{- include "charts-library.initContainers" . | nindent 6 }}
      containers:
        - name: {{ $containerName }}
          image: "{{ .Values.image.uri | default (printf \"%s.dkr.ecr.%s.amazonaws.com/%s/%s:%s\" .Values.repository.accountId .Values.repository.region .Values.environment.name .Values.application.name .Values.image.tag) }}"
          {{- if and (hasKey .Values "variables") (not (empty .Values.variables)) }}
          envFrom:
            - configMapRef:
                name: {{ include "charts-library.configmapenvName" . }}
          {{- end }}
          {{- if .Values.volumes.enable }}
          volumeMounts:
            {{- if and (hasKey .Values "volume") (not (empty .Values.volume)) }}
            - name: {{ $app }}-volume
              mountPath: {{ .Values.volume.mountPath }}
              readOnly: {{ .Values.volume.readOnly | default false }}
            {{- end }}
            {{- if and (hasKey .Values "config") (not (empty .Values.config)) }}
            - name: {{ .Values.config.name | default (printf "%s-config" $app) }}
              mountPath: {{ .Values.config.mountPath }}
              readOnly: {{ .Values.config.readOnly | default true }}
            {{- end }}
          {{- end }}
          {{- if .Values.service.enable }}
          ports:
            {{- range .Values.ports }}
            - containerPort: {{ .containerPort }}
              name: {{ .name | default (printf "%s-port" $app) | trunc 63 | trimSuffix "-" }}
              protocol: {{ .protocol | upper | default "TCP" }}
            {{- end }}
          {{- end }}
          {{- if .Values.serviceAccount.enable }}
          serviceAccountName: {{ include "charts-library.serviceAccountName" . }}
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
      {{- if .Values.volumes.enable }}
      volumes:
        {{- if and (hasKey .Values "config") (not (empty .Values.config)) }}
        - name: {{ .Values.config.name | default (printf "%s-config" $app) }}
          configMap:
            name: {{ include "charts-library.configmapName" . }}
        {{- end }}
        {{- if and (hasKey .Values "volume") (not (empty .Values.volume)) }}
        - name: {{ $app }}-volume
          emptyDir: {}
        {{- end }}
      {{- end }}

  volumeClaimTemplates:
    - metadata:
        name: {{ $pvcName }}
      spec:
        accessModes: [ "{{ .Values.volume.accessMode }}" ]
        storageClassName: {{ $storageClass }}
        resources:
          requests:
            storage: {{ .Values.volume.size }}

{{- end }}
{{- end -}}
