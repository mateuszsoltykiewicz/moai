{{/*
targetgroup

This template defines an AWS Load Balancer Controller TargetGroupBinding resource.

- Rendered only if `.Values.targetGroup.enable` is true.
- Binds a Kubernetes Service to an AWS ALB Target Group for ingress traffic routing.
- All required values must be set explicitly in values.yaml; no defaults are used.
- Naming follows the pattern: <environment>-<application>-targetgroupbinding.
- Namespace follows the pattern: <environment>-<namespace>.
- Standard labels are included via the "labels" helper template.

Usage: {{ include "targetgroup" . | nindent }}

See: https://kubernetes-sigs.github.io/aws-load-balancer-controller/latest/guide/targetgroupbinding/targetgroupbinding/
*/}}

{{- define "targetgroup" -}}
{{- if and (hasKey .Values "targetGroup") (.Values.targetGroup.enable) }}

apiVersion: elbv2.k8s.aws/v1beta1
kind: TargetGroupBinding
metadata:
  # TargetGroupBinding name is dynamically generated from environment and application names.
  name: {{ printf "%s-%s-targetgroupbinding" (.Values.environment.name | lower | replace " " "-") (.Values.application.name | lower | replace " " "-") | quote }}
  # Namespace for the resource, built from environment and namespace names.
  namespace: {{ printf "%s-%s" (.Values.environment.name | lower | replace " " "-") (.Values.namespace.name | lower | replace " " "-") | quote }}
  labels:
    # Standard labels for resource tracking and selection.
    {{- include "labels" . | nindent 4 }}

spec:
  serviceRef:
    # Reference to the Kubernetes Service to bind to the target group.
    # This service must exist in the same namespace.
    name: {{ printf "%s-%s-service" (.Values.environment.name | lower | replace " " "-") (.Values.application.name | lower | replace " " "-") | quote }}
    port: {{ .Values.application.container.port.containerPort }}
  # ARN of the AWS Target Group to bind.
  # This must be an existing Target Group in your AWS account.
  targetGroupARN: {{ .Values.targetGroup.arn | quote }}

  # Optionally, you can add fields like targetType, vpcID, or nodeSelector if needed.
  # See AWS docs for advanced usage.

{{- end }}
{{- end -}}
