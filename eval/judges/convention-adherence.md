You are evaluating whether an AI coding agent followed the repository-specific conventions of a Kubernetes operator codebase when implementing a task.

## Reference Implementation (Task + Expected Approach)
{{ outputs.annotation_reference_content }}

## Agent's Implementation
{{ conversation }}

## Repository Conventions to Check

### multiarch-tuning-operator conventions
- **Metric naming**: New controller metrics must use the `mto_ppo_ctrl_*` prefix; webhook metrics use `mto_ppo_wh_*`
- **Ginkgo test structure**: Tests use `Describe/Context/It` BDD hierarchy with `ginkgo.It`, not raw `func Test*` or `t.Run`
- **Fluent builder API**: Test code creates Kubernetes objects using `pkg/testing/builder` fluent builders (e.g., `builder.NewPod().WithName(...).Build()`), not raw struct literals like `&corev1.Pod{ObjectMeta: metav1.ObjectMeta{...}}`
- **Code generation order**: `make manifests` MUST precede `make generate` — they are not interchangeable and cannot be combined in one step
- **CPPC access pattern**: Controllers access the singleton `ClusterPodPlacementConfig` through the informer package (`pkg/informers/clusterpodplacementconfig/`), never via direct Kubernetes API calls from the controller
- **Execution mode conventions**: Each binary mode has its own leader election ID string; modes are mutually exclusive via `bindFlags` in `cmd/main.go`

### cert-manager-operator conventions
- **Singleton enforcement**: Cluster-scoped singleton types enforce the `metadata.name == 'cluster'` constraint via CEL `x-kubernetes-validations` markers at the API level, not in controller logic
- **Deployment mutation pattern**: Mutations to operand Deployments are named Go functions chained in a pipeline; a defensive `validateDeploymentManifest` call guards the pipeline by verifying required container names and volumes exist before mutation
- **OptionalInformer pattern**: Informers for APIs that may not exist (e.g., OpenShift-specific APIs) use `InitInformerIfAvailable[T]` from `pkg/operator/utils/apidiscovery.go`, and all code paths guard on `Applicable()` before using the informer
- **Image source**: Container image references ALWAYS come from `RELATED_IMAGE_*` environment variables, never hardcoded or from CRD spec fields
- **Hash-triggered restarts**: Rolling restarts triggered by ConfigMap content changes use SHA-256 hash of the PEM content (not `resourceVersion`) stamped as a pod template annotation

## Scoring Rubric

**5 — Fully idiomatic**: The implementation follows all applicable conventions exactly. A senior maintainer of this repo would not leave convention-related comments in code review.

**4 — Mostly idiomatic**: 1 minor convention deviation (e.g., uses wrong metric prefix once, or forgets the builder API for one test case while using it correctly elsewhere).

**3 — Partially idiomatic**: The approach is recognizable but has multiple convention gaps (e.g., writes raw pod literals in tests instead of using the builder, or states make targets in wrong order, or reads CPPC directly from API instead of informer).

**2 — Convention-unaware**: The implementation ignores most conventions specific to this codebase (e.g., no builder API usage, wrong metric naming, wrong CPPC access pattern, missing singleton CEL enforcement).

**1 — Convention-unaware and generic**: Shows no awareness of any codebase-specific patterns; implementation looks like it was written for a generic Kubernetes operator with no knowledge of this repo's structure.

Respond in this format:
Score: <integer 1-5>
Justification: <2-3 sentences identifying which conventions were followed and which were missed>
