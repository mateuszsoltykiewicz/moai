{{/*
rolebinding

This template defines a Kubernetes RoleBinding for the application.

- Rendered only if `.Values.role.enable` is true.
- The RoleBinding binds the generated Role to a ServiceAccount in the specified namespace.
- All values must be set explicitly in values.yaml; no defaults are used.
- Naming follows the pattern: <environment>-<application>-rolebinding.
- Namespace follows the pattern: <environment>-<namespace>.
- Standard labels are included via the "labels" helper template.

Usage: {{ include "rolebinding" . }}
*/}}

{{- define "rolebinding" -}}
{{- if .Values.role.enable }}

apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  # RoleBinding name is dynamically generated from environment and application names.
  name: {{ printf "%s-%s-rolebinding" (.Values.environment.name | lower) (.Values.application.name | lower | replace " " "-") | quote }}
  # Namespace for the RoleBinding, built from environment and namespace names.
  namespace: {{ printf "%s-%s" (.Values.environment.name | lower) (.Values.namespace.name | lower) | quote }}
  labels:
    {{- include "labels" . | nindent 4 }}

subjects:
  # This subject binds the Role to the application's ServiceAccount in the same namespace.
  - kind: ServiceAccount
    name: {{ printf "%s-%s-serviceaccount" (.Values.environment.name | lower) (.Values.application.name | lower | replace " " "-") | quote }}
    namespace: {{ printf "%s-%s" (.Values.environment.name | lower) (.Values.namespace.name | lower) | quote }}

roleRef:
  # Reference to the Role created by the role template.
  kind: Role
  name: {{ printf "%s-%s-role" (.Values.environment.name | lower) (.Values.application.name | lower | replace " " "-") | quote }}
  apiGroup: rbac.authorization.k8s.io

{{- end }}
{{- end -}}
