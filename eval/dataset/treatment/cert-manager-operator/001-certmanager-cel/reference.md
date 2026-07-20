# Reference: Add CEL Singleton Enforcement to CertManager

## File to Modify: `api/operator/v1alpha1/certmanager_types.go`

Add this kubebuilder marker directly above the `CertManager` struct definition,
matching the pattern already used on `TrustManager`:

```go
// +kubebuilder:validation:XValidation:rule="self.metadata.name == 'cluster'",message="CertManager.operator.openshift.io/v1alpha1 is a singleton, .metadata.name must be 'cluster'"
// +kubebuilder:object:root=true
// +kubebuilder:subresource:status
// +kubebuilder:resource:scope=Cluster
type CertManager struct {
    metav1.TypeMeta   `json:",inline"`
    metav1.ObjectMeta `json:"metadata,omitempty"`
    // ...
}
```

## Key Details
- The marker syntax is `+kubebuilder:validation:XValidation:rule="<CEL>",message="<msg>"`
- The CEL expression is `self.metadata.name == 'cluster'` (single quotes around 'cluster')
- `self` refers to the object being validated in CEL
- The message should follow the pattern used by TrustManager's message in the same file

## Make Target
```
make manifests
```
This regenerates the CRD YAML in config/crd/bases/ and must be followed by copying
or regenerating the bundle CRD in bundle/manifests/.

## Context
This closes a known gap: TrustManager and IstioCSR already have this CEL enforcement,
but CertManager historically relied on convention (always create named 'cluster').
Adding the CEL rule makes the constraint machine-enforceable at admission time.

## Score 5 Criteria
- Correct XValidation marker syntax (not `+kubebuilder:validation:Enum` or similar)
- CEL rule uses `self.metadata.name == 'cluster'` (single quotes, not double)
- Marker placed above the struct declaration (not inside it)
- `make manifests` identified as the required command
- Message text is consistent with TrustManager's existing message pattern
