# Helm Chart for Kubernetes Application Deployment

This Helm chart provides a robust, highly configurable framework for deploying applications to Kubernetes using strict naming conventions, explicit value requirements, and best practices for security and maintainability.

## Features

- **Strict naming conventions:** All resources are named using `<environment>-<application>-<resource>` or `<environment>-<namespace>` patterns.
- **Explicit configuration:** No defaults—**all values must be set explicitly** in `values.yaml`.
- **Modular templates:** Supports Deployments, StatefulSets, Services, Ingress, ConfigMaps, Secrets, RBAC, HPA, PDB, Storage, AWS IRSA, and more.
- **Consistent labels:** Uses a `labels` helper for standard Kubernetes labels across all resources.
- **AWS integration:** Supports IAM Roles for Service Accounts (IRSA) and TargetGroupBinding for AWS Load Balancer Controller.
- **Best practices:** Follows Kubernetes and Helm best practices for resource management, security, and extensibility.

---

## Getting Started

### 1. **Clone the Chart**

git clone <your-repo-url>
cd <your-chart-directory>


### 2. **Configure `values.yaml`**

All values are **required**. Example structure:

### 3. **Install the Chart**

helm install my-release . -f values.yaml

### 4. **Upgrade the Chart**

helm upgrade my-release . -f values.yaml

---

## Templates Overview

| Template File               | Purpose                                                                |
|-----------------------------|------------------------------------------------------------------------|
| `Deployment.tpl`            | Standard Kubernetes Deployment                                         |
| `StatefulSet.tpl`           | StatefulSet for stateful workloads                                     |
| `Service.tpl`               | ClusterIP/Headless Service for app discovery                           |
| `Ingress.tpl`               | Ingress resource for HTTP routing                                      |
| `ConfigMap.tpl`             | Application configuration                                              |
| `ConfigMapEnv.tpl`          | Environment variables as ConfigMap                                     |
| `Secrets.tpl`               | Kubernetes Secrets for sensitive data                                  |
| `Namespace.tpl`             | Namespace creation (if enabled)                                        |
| `Role.tpl`                  | Namespaced RBAC Role                                                   |
| `RoleBinding.tpl`           | RoleBinding for ServiceAccount                                         |
| `ClusterRole.tpl`           | Cluster-wide RBAC Role                                                 |
| `ClusterRoleBinding.tpl`    | ClusterRoleBinding for group access                                    |
| `ServiceAccount.tpl`        | ServiceAccount with IRSA annotation                                    |
| `HorizontalPodAutoscaling.tpl` | HPA for automatic scaling                                           |
| `PodDisruptionBudget.tpl`   | PDB for high availability                                              |
| `PersistentVolume.tpl`      | PersistentVolume for stateful workloads                                |
| `StorageClass.tpl`          | StorageClass for dynamic provisioning                                  |
| `TargetGroupBinding.tpl`    | AWS TargetGroupBinding for ALB/NLB integration                        |
| `NetworkPolicy.tpl`         | NetworkPolicy for traffic control                                      |
| `livenessProbe.tpl`         | Liveness probe configuration                                           |
| `readinessProbe.tpl`        | Readiness probe configuration                                          |
| `Resources.tpl`             | Resource requests and limits                                           |
| `Labels.tpl`                | Standardized labels helper                                             |

---

## Best Practices

- **No defaults:** All required values must be set in `values.yaml` to avoid silent misconfigurations.
- **Consistent naming:** Use the same naming patterns for all resources for clarity and uniqueness.
- **Explicit RBAC:** Only enable and configure RBAC resources as needed.
- **Secure secrets:** Use `kubectl create secret` or SOPS for managing sensitive values.
- **Use `helm lint`:** Always run `helm lint .` before deploying to catch template errors.
- **Version control:** Keep your chart and values files in Git for auditability and collaboration.

---

## AWS Integration

- **IRSA:** ServiceAccount templates are ready for AWS IAM Roles for Service Accounts.
- **TargetGroupBinding:** Easily integrate with AWS Load Balancer Controller for ingress traffic.

---

## Troubleshooting

- **Helm fails to render:** Check for missing required values in `values.yaml`.
- **Resource name collisions:** Ensure unique values for `environment.name`, `application.name`, and `namespace.name`.
- **RBAC issues:** Verify that ServiceAccounts, Roles, and RoleBindings are enabled and named correctly.

---

## Contributing

Feel free to open issues or submit pull requests to improve this chart.  
Please follow the established naming and structure conventions.

---

## License

[MIT](LICENSE)

---

## References

- [Helm Documentation](https://helm.sh/docs/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [AWS EKS IRSA](https://docs.aws.amazon.com/eks/latest/userguide/iam-roles-for-service-accounts.html)
- [AWS Load Balancer Controller](https://kubernetes-sigs.github.io/aws-load-balancer-controller/latest/)

---
