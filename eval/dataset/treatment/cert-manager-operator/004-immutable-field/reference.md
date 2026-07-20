# Reference: Add tlsMinVersion Immutable Field to IstioCSR

## In `api/operator/v1alpha1/istiocsr_types.go`

Add to the `IstioCSRConfig` struct (or the parent `IstioCSRSpec`):

```go
// TLSMinVersion defines the minimum TLS version. Once set, this field is immutable.
// +kubebuilder:validation:Optional
// +kubebuilder:validation:Enum=VersionTLS12;VersionTLS13
// +kubebuilder:validation:XValidation:rule="!has(oldSelf.tlsMinVersion) || has(self.tlsMinVersion)",message="tlsMinVersion is immutable once set"
// +kubebuilder:validation:XValidation:rule="!has(self.tlsMinVersion) || self.tlsMinVersion == oldSelf.tlsMinVersion",message="tlsMinVersion value is immutable"
TLSMinVersion *string `json:"tlsMinVersion,omitempty"`
```

## CEL Rule Explanation

Two separate `XValidation` markers handle the two immutability cases:

1. **Presence-immutability** (`!has(oldSelf.field) || has(self.field)`):
   - If `oldSelf` doesn't have the field (it was absent), this rule is satisfied regardless of `self`
   - If `oldSelf` has the field (it was set), then `self` must also have it (cannot remove)
   - This prevents: set → unset transitions

2. **Value-immutability** (`!has(self.field) || self.field == oldSelf.field`):
   - If `self` doesn't have the field (it's absent), trivially satisfied
   - If `self` has the field, it must equal `oldSelf.field`
   - This prevents: changing the value once set

These are the same two-rule pattern used for `IssuerRef` and `privateKeyAlgorithm` in
the same file — the agent should look for existing examples.

## Mutation Pipeline Update in `pkg/controller/istiocsr/deployments.go`

Add a new mutation function:
```go
func updateTLSMinVersion(istiocsr *operatorv1alpha1.IstioCSR) deploymentMutationFunc {
    return func(deployment *appsv1.Deployment) error {
        if istiocsr.Spec.IstioCSRConfig.TLSMinVersion == nil {
            return nil
        }
        for i, c := range deployment.Spec.Template.Spec.Containers {
            if c.Name == istiocsrContainerName {
                deployment.Spec.Template.Spec.Containers[i].Args = append(
                    deployment.Spec.Template.Spec.Containers[i].Args,
                    "--tls-min-version="+*istiocsr.Spec.IstioCSRConfig.TLSMinVersion,
                )
                return nil
            }
        }
        return fmt.Errorf("container %q not found", istiocsrContainerName)
    }
}
```

Chain it in the mutation pipeline list.

## Score 5 Criteria
- Two separate XValidation markers (not one combined rule)
- Correct CEL `has()` syntax for presence checking
- Enum values match Go constant names exactly (VersionTLS12, VersionTLS13)
- Pointer type (`*string`) for optional field
- Mutation function follows the typed function pattern, chained in the pipeline
