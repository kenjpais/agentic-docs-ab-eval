# Reference: Add MaxImageInspectionRetries Field

## Files to Modify

### 1. `api/v1beta1/clusterpodplacementconfig_types.go`
Add to `ClusterPodPlacementConfigSpec`:
```go
// MaxImageInspectionRetries is the maximum number of times the operator will
// retry image inspection before marking the pod as failed.
// +kubebuilder:validation:Optional
// +kubebuilder:validation:Minimum=1
// +kubebuilder:validation:Maximum=20
// +kubebuilder:default=5
MaxImageInspectionRetries *int32 `json:"maxImageInspectionRetries,omitempty"`
```

### 2. `api/v1alpha1/` — Conversion
v1alpha1 does NOT get the new field. The conversion function
`Convert_v1beta1_ClusterPodPlacementConfigSpec_To_v1alpha1_ClusterPodPlacementConfigSpec`
must explicitly ignore the field (or controller-gen generates a compile error about unhandled fields).
Add a comment explaining the field is intentionally dropped in v1alpha1.

### 3. `internal/controller/podplacement/pod_model.go`
Replace any hardcoded retry constant with a read from the CPPC informer:
```go
cppc := cppcInformer.GetClusterPodPlacementConfig()
maxRetries := int32(5) // fallback default
if cppc != nil && cppc.Spec.MaxImageInspectionRetries != nil {
    maxRetries = *cppc.Spec.MaxImageInspectionRetries
}
```
The informer is injected into the reconciler — it should already be accessible in pod_model.go's context.

## Make Target Order
```
make manifests   # FIRST: regenerates CRD YAML and webhook configs from kubebuilder markers
make generate    # SECOND: regenerates deepcopy functions, conversion stubs, client code
```
Running `make generate` before `make manifests` fails because generate depends on the updated CRD.
These targets are NOT interchangeable and CANNOT be combined into a single step.

## Key Conventions
- Optional fields use pointer types (`*int32`) to distinguish "not set" from zero value
- Default values set via `+kubebuilder:default` marker, not in Go initialization code
- CPPC is NEVER fetched via direct API call from controllers — always via the informer singleton
- `make manifests` precedes `make generate` — this ordering is critical and non-obvious

## Score 5 Criteria
- `*int32` pointer type with all three markers (Minimum=1, Maximum=20, default=5)
- `make manifests` stated before `make generate`, with explanation of why
- Informer access pattern used (not `k8sClient.Get(...)`)
- Conversion function updated to handle the new field (even if just an ignore comment)
