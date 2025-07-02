ApplicationCharts
=================

This directory contains the Helm charts for all microservices in the platform.
Each microservice is located in its own subdirectory and uses a shared ChartsLibrary for reusable Kubernetes resource templates.

Directory Structure
-------------------

/Helm/ApplicationCharts/
├── AlarmsServer/
│   ├── Chart.yaml
│   ├── values.yaml
│   └── templates/
│       ├── deployment.yaml
│       ├── service.yaml
│       └── ...
├── BankManager/
│   └── ...
├── StateServer/
│   └── ...
└── ...

How It Works
------------

- Each microservice has its own Helm chart (subdirectory).
- All charts use templates from the ../ChartsLibrary via Helm dependencies.
- Templates in each chart are thin wrappers that simply include library templates, for example:
    {{ include "charts-library.deployment" . }}
- All core logic and best practices (naming, RBAC, probes, storage, etc.) are centralized in the library for consistency and maintainability.

Microservice Groups & Template Sets
-----------------------------------

Microservices are grouped by workload type, each with a standard set of templates:

A. Stateless Web/API Services
    Examples: AlarmsServer, BankManager, ExceptionsServer, HomeKitBridge, etc.
    Templates: deployment, service, configmapenv, secrets, ingress, hpa, pdb, serviceaccount, rbac, networkpolicy, servicemonitor, initcontainers, rollout

B. Stateful Services
    Examples: StateServer
    Templates: statefulset, service (headless), configmapenv, secrets, persistentvolume, storageclass, pdb, serviceaccount, rbac, networkpolicy, servicemonitor, initcontainers, rollout

C. Batch/Job Services
    Examples: HeatingJob, SecretsRotator (if run as a Job)
    Templates: job, configmapenv, secrets, serviceaccount, rbac, networkpolicy, initcontainers

How to Add a New Microservice Chart
-----------------------------------

1. Copy the appropriate template set (see above) into your new chart’s /templates directory.
2. Add and customize values.yaml with service-specific configuration (ports, env, resources, etc.).
3. Reference ChartsLibrary as a dependency in Chart.yaml:
    dependencies:
      - name: charts-library
        version: 1.0.0
        repository: "file://../../ChartsLibrary"
4. Run helm dependency update in the chart directory.

Best Practices
--------------

- All Docker images must be built for ARM64 for Raspberry Pi clusters.
- Use MicroK8s hostpath storage class for all persistent volumes.
- Set nodeSelector for ARM64 in values.yaml:
    nodeSelector:
      kubernetes.io/arch: arm64
- Use ServiceMonitor only if Prometheus is enabled in your cluster.
- Use NetworkPolicy for microservice isolation and security.
- Validate charts with helm lint and helm template before deploying.
- Document any special requirements in each chart’s README.md.

Deployment Workflow
-------------------

1. Build and push ARM64 Docker images for each microservice.
2. Update values.yaml as needed for each deployment.
3. Deploy with Helm:
    microk8s helm3 upgrade --install <service> ./Helm/ApplicationCharts/<Service> \
      --namespace <namespace> \
      -f ./Helm/ApplicationCharts/<Service>/values.yaml

Contributing
------------

- Add new microservices by following the group template sets.
- Update ChartsLibrary for any shared improvements or fixes.
- Test all charts in a staging MicroK8s cluster before production rollout.

References
----------

- Helm Documentation: https://helm.sh/docs/
- MicroK8s Documentation: https://microk8s.io/docs
- Kubernetes Best Practices: https://kubernetes.io/docs/concepts/overview/working-with-objects/common-labels/

This structure ensures a scalable, maintainable, and production-ready Kubernetes platform for your microservices on MicroK8s and ARM hardware.

If you have questions or want to add a new service, see the template sets above or ask the platform team for guidance.
