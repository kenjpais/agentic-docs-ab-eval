# Reference: Fix NetworkPolicy Infinite Reconcile Loop

## File to Modify

`pkg/controller/certmanager/cert_manager_networkpolicy.go`

## Change 1: Add resourceCache Field to Struct

```go
type CertManagerNetworkPolicyUserDefinedController struct {
    operatorClient               v1helpers.OperatorClient
    certManagerOperatorInformers certmanoperatorinformers.SharedInformerFactory
    kubeClient                   kubernetes.Interface
    kubeInformersForNamespaces   v1helpers.KubeInformersForNamespaces
    eventRecorder                events.Recorder
    resourceCache                resourceapply.ResourceCache  // add this field
}
```

## Change 2: Initialize resourceCache in Constructor

In `newCertManagerNetworkPolicyUserDefinedController`, add to the struct literal:

```go
resourceCache: resourceapply.NewResourceCache(),
```

## Change 3: Rewrite createOrUpdateNetworkPolicy

Replace the manual Get+Update with `ApplyNetworkPolicy`:

```go
func (c *CertManagerNetworkPolicyUserDefinedController) createOrUpdateNetworkPolicy(
    ctx context.Context, policy *networkingv1.NetworkPolicy) error {
    _, _, err := resourceapply.ApplyNetworkPolicy(
        ctx,
        c.kubeClient.NetworkingV1(),
        c.eventRecorder,
        policy,
        c.resourceCache,
    )
    if err != nil {
        return fmt.Errorf("failed to apply network policy: %w", err)
    }
    return nil
}
```

## Why This Fixes the Loop

`resourceapply.ApplyNetworkPolicy` computes a diff between desired and existing. If
nothing changed, it skips the Update call. No Update → no watch event → no re-queue.
The ResourceCache avoids a redundant API GET on repeated reconciles.

## No Make Target Required

Pure Go source change.

## Score-5 Criteria

- `resourceCache resourceapply.ResourceCache` field added to struct
- `resourceapply.NewResourceCache()` called in constructor
- `createOrUpdateNetworkPolicy` body replaced with `resourceapply.ApplyNetworkPolicy()`
  call using all five arguments: ctx, kubeClient.NetworkingV1(), eventRecorder, policy, resourceCache
- Error wrapped with `fmt.Errorf("failed to apply network policy: %w", err)`
- No other logic changed
