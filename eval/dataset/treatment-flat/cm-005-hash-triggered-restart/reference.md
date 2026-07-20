# Reference: Hash-Triggered Rolling Restart for IstioCSR

## Pattern Source
`pkg/controller/trustmanager/configmaps.go` — this is the authoritative reference.
The implementation must mirror it, not invent a new approach.

## Implementation in `pkg/controller/istiocsr/`

New file or addition to existing configmaps.go:

```go
const caBundleAnnotation = "operator.openshift.io/cert-manager-bundle-hash"

// reconcileCABundle reads the CNO-injected CA ConfigMap, computes a SHA-256 hash
// of the PEM content, and stamps it on the IstioCSR Deployment pod template.
func (r *IstioCSRReconciler) reconcileCABundle(
    ctx context.Context,
    istiocsr *operatorv1alpha1.IstioCSR,
    deployment *appsv1.Deployment,
) error {
    cm := &corev1.ConfigMap{}
    if err := r.Client.Get(ctx, types.NamespacedName{
        Namespace: istiocsr.Namespace,
        Name:      caBundleConfigMapName, // the CNO-injected configmap name
    }, cm); err != nil {
        return fmt.Errorf("failed to get CA bundle ConfigMap: %w", err)
    }

    // Idempotency guard: skip if content unchanged
    pemData := cm.Data["ca-bundle.crt"] // or the appropriate key
    h := sha256.Sum256([]byte(pemData))
    hash := fmt.Sprintf("%x", h)

    currentHash := deployment.Spec.Template.Annotations[caBundleAnnotation]
    if currentHash == hash {
        return nil // no change, skip patch
    }

    // Stamp the hash on the pod template (triggers rolling restart)
    if deployment.Spec.Template.Annotations == nil {
        deployment.Spec.Template.Annotations = make(map[string]string)
    }
    deployment.Spec.Template.Annotations[caBundleAnnotation] = hash

    return r.Client.Update(ctx, deployment)
}
```

## Critical Correctness Points

1. **Hash the PEM content, NOT `resourceVersion`**: Hashing `resourceVersion` causes
   unnecessary restarts when the ConfigMap is updated for metadata reasons without
   content changes. Hashing the PEM content is idempotent across metadata-only updates.

2. **Idempotency guard with `maps.Equal` or direct comparison**: Check current annotation
   against new hash BEFORE patching. Skip if equal. TrustManager uses this pattern — it is
   not optional.

3. **Annotation on `Deployment.Spec.Template`**, not on `Deployment.ObjectMeta`:
   The annotation must be on the pod template to trigger a rolling restart of pods.
   Annotating the Deployment itself does not restart pods.

4. **SHA-256** (not MD5, not SHA-1): Use `crypto/sha256`.

## Score 5 Criteria
- Hash of PEM content (not resourceVersion)
- Idempotency guard (skips patch if hash unchanged)
- Annotation placed on Deployment.Spec.Template.Annotations (pod template)
- Uses SHA-256 (`crypto/sha256`)
- Mirrors TrustManager's pattern structure (not a novel approach)
