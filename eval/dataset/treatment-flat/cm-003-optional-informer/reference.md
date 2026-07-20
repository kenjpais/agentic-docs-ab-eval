# Reference: NewProxyInformerIfAvailable

## In `pkg/operator/utils/apidiscovery.go`

Follow the existing `InitInformerIfAvailable[T]` generic function. Add:

```go
func NewProxyInformerIfAvailable(
    ctx context.Context,
    discoveryClient discovery.DiscoveryInterface,
    configInformerFactory configinformers.SharedInformerFactory,
) (OptionalInformer[configinformers.SharedInformerFactory], error) {
    return InitInformerIfAvailable[configinformers.SharedInformerFactory](
        ctx,
        discoveryClient,
        "config.openshift.io",
        "v1",
        "proxies",
        configInformerFactory,
    )
}
```

## Threading through TrustManager controller

In `pkg/controller/trustmanager/controller.go`, add `proxyInformer` field to the reconciler struct:
```go
type TrustManagerReconciler struct {
    // ... existing fields
    proxyInformer utils.OptionalInformer[configinformers.SharedInformerFactory]
}
```

Update the constructor to accept it. In `Reconcile()`:
```go
if r.proxyInformer.Applicable() {
    proxy, err := r.proxyInformer.Informer().Config().V1().Proxies().Lister().Get("cluster")
    if err != nil && !apierrors.IsNotFound(err) {
        return ctrl.Result{}, fmt.Errorf("failed to get cluster proxy: %w", err)
    }
    if proxy != nil {
        // Use proxy.Spec.HTTPSProxy, proxy.Spec.HTTPProxy, proxy.Spec.NoProxy
    }
}
```

## Critical Pattern: OptionalInformer Contract
- ALWAYS guard with `Applicable()` before using the informer — never call `.Informer()` unconditionally
- `InitInformerIfAvailable` calls `ServerResourcesForGroupVersion` and returns `Applicable() == false` on 404 (API absent)
- On non-404 errors, it returns the error (fatal) — do NOT silently ignore
- This pattern allows the operator to run on MicroShift and vanilla Kubernetes where OpenShift APIs are absent

## Score 5 Criteria
- Uses `InitInformerIfAvailable[T]` generic (does not reimplement API discovery)
- Correct GVR: `config.openshift.io/v1/proxies`
- `Applicable()` guard in reconciler before any informer access
- Threaded through constructor (not a package-level global)
- Error from `NewProxyInformerIfAvailable` is propagated (not ignored)
