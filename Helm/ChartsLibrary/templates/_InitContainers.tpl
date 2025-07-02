{{/*
charts-library.initContainers

Renders a list of initContainers if defined in values.yaml.
Usage: {{ include "charts-library.initContainers" . | nindent }}
*/}}

{{- define "charts-library.initContainers" -}}
{{- $init := (default list .Values.initContainers) }}
{{- if and $init (gt (len $init) 0) }}
initContainers:
  {{- range $init }}
  - name: {{ .name | quote }}
    image: {{ .image | quote }}
    {{- if .command }}
    command:
      {{- range .command }}
      - {{ . | quote }}
      {{- end }}
    {{- end }}
    {{- if .args }}
    args:
      {{- range .args }}
      - {{ . | quote }}
      {{- end }}
    {{- end }}
    {{- if .env }}
    env:
      {{- range .env }}
      - name: {{ .name | quote }}
        value: {{ .value | quote }}
      {{- end }}
    {{- end }}
    {{- if .envFrom }}
    envFrom:
      {{- toYaml .envFrom | nindent 6 }}
    {{- end }}
    {{- if .volumeMounts }}
    volumeMounts:
      {{- toYaml .volumeMounts | nindent 6 }}
    {{- end }}
  {{- end }}
{{- end }}
{{- end -}}
