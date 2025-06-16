{{/*
statefulset

This template defines a Kubernetes StatefulSet for stateful applications requiring stable storage and identities.

- Rendered only if `.Values.application.type` is "statefulset".
- Includes persistent volume claims, probes, and AWS ECR integration.
- All required values must be set explicitly in values.yaml; no defaults are used.
- Naming follows the pattern: <environment>-<application>-statefulset.
- Namespace follows the pattern: <environment>-<namespace>.
- Standard labels are included via the "labels" helper template.

Usage: {{ include "statefulset" . | nindent }}
*/}}

{{- define "statefulset" -}}
{{- if eq (lower .Values.application.type) "statefulset" }}

apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: {{ printf "%s-%s-statefulset" (.Values.environment.name | lower | replace " " "-") (.Values.application.name | lower | replace " " "-") | quote }}
  namespace: {{ printf "%s-%s" (.Values.environment.name | lower | replace " " "-") (.Values.namespace.name | lower | replace " " "-") | quote }}
  labels:
    {{- include "labels" . | nindent 4 }}
    app.kubernetes.io/name: {{ printf "%s-%s-statefulset" (.Values.environment.name | lower | replace " " "-") (.Values.application.name | lower | replace " " "-") | quote }}

spec:
  selector:
    matchLabels:
      app.kubernetes.io/name: {{ printf "%s-%s-statefulset" (.Values.environment.name | lower | replace " " "-") (.Values.application.name | lower | replace " " "-") | quote }}
      namespace: {{ printf "%s-%s" (.Values.environment.name | lower | replace " " "-") (.Values.namespace.name | lower | replace " " "-") | quote }}
      environment: {{ .Values.environment.name | lower | quote }}
  serviceName: {{ printf "%s-%s-service" (.Values.environment.name | lower | replace " " "-") (.Values.application.name | lower | replace " " "-") | quote }}
  replicas: {{ .Values.replicaCount }}
  minReadySeconds: 10

  template:
    metadata:
      labels:
        {{- include "labels" . | nindent 8 }}
        app.kubernetes.io/name: {{ printf "%s-%s-statefulset" (.Values.environment.name | lower | replace " " "-") (.Values.application.name | lower | replace " " "-") | quote }}
        namespace: {{ printf "%s-%s" (.Values.environment.name | lower | replace " " "-") (.Values.namespace.name | lower | replace " " "-") | quote }}
        environment: {{ .Values.environment.name | lower | quote }}
    spec:
      terminationGracePeriodSeconds: 10
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
            {{- if and (hasKey .Values "volume") (not (empty .Values.volume)) }}
            - name: {{ printf "%s-%s-volume" (.Values.environment.name | lower | replace " " "-") (.Values.application.name | lower | replace " " "-") | quote }}
              mountPath: {{ .Values.volume.mountPath }}
              readOnly: {{ .Values.volume.readOnly }}
            {{- end }}
            {{- if and (hasKey .Values "config") (not (empty .Values.config)) }}
            - name: {{ .Values.config.name }}
              mountPath: {{ .Values.config.mountPath }}
              readOnly: {{ .Values.config.readOnly }}
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

          {{- if .Values.serviceAccount.enable }}
          serviceAccountName: {{ printf "%s-%s-serviceaccount" (.Values.environment.name | lower | replace " " "-") (.Values.application.name | lower | replace " " "-") | quote }}
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

      {{- if .Values.volumes.enable }}
      volumes:
        {{- if and (hasKey .Values "config") (not (empty .Values.config)) }}
        - name: {{ .Values.config.name }}
          configMap:
            name: {{ printf "%s-%s-configmap" (.Values.environment.name | lower | replace " " "-") (.Values.application.name | lower | replace " " "-") | quote }}
        {{- end }}
        {{- if and (hasKey .Values "volume") (not (empty .Values.volume)) }}
        - name: {{ printf "%s-%s-volume" (.Values.environment.name | lower | replace " " "-") (.Values.application.name | lower | replace " " "-") | quote }}
          emptyDir: {}
        {{- end }}
      {{- end }}

  volumeClaimTemplates:
    - metadata:
        name: {{ printf "%s-%s-pvc" (.Values.environment.name | lower | replace " " "-") (.Values.application.name | lower | replace " " "-") | quote }}
      spec:
        accessModes: [ "{{ .Values.volume.accessMode }}" ]
        storageClassName: {{ printf "%s-%s-storageclass" (.Values.environment.name | lower | replace " " "-") (.Values.application.name | lower | replace " " "-") | quote }}
        resources:
          requests:
            storage: {{ .Values.volume.size }}

{{- end }}
{{- end -}}
