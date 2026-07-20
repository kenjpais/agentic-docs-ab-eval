# Reference: Webhook Validation for Duplicate Architectures

## Files to Modify

### `api/v1beta1/clusterpodplacementconfig_webhook.go`

In `ValidateCreate` and `ValidateUpdate`, add:
```go
if cppc.Spec.Plugins != nil &&
    cppc.Spec.Plugins.NodeAffinityScoring != nil {
    if err := cppc.Spec.Plugins.NodeAffinityScoring.ValidateArchitecturesSet(); err != nil {
        allErrs = append(allErrs, field.Invalid(
            field.NewPath("spec", "plugins", "nodeAffinityScoring", "platforms"),
            cppc.Spec.Plugins.NodeAffinityScoring.Platforms,
            err.Error(),
        ))
    }
}
```

Return `allErrs.ToAggregate()` if non-empty (following existing webhook error pattern).

## Why the Webhook (Not the Controller)
Validation belongs in the webhook's `ValidateCreate`/`ValidateUpdate`, not the controller's
reconciler. The webhook enforces correctness at admission time, preventing bad objects from
entering etcd. The controller should not need to defensively validate its own input.
This is the "singleton configuration" security principle: the CPPC is cluster-wide, so
bad configuration must be rejected before it can affect the entire cluster.

## Unit Test
```go
Describe("ValidateCreate", func() {
    Context("with duplicate architectures in NodeAffinityScoring", func() {
        It("should reject the object", func() {
            cppc := builder.NewClusterPodPlacementConfig().
                WithNodeAffinityScoring([]commonv1alpha1.Platform{
                    {Architecture: "amd64"},
                    {Architecture: "amd64"}, // duplicate
                }).
                Build()
            _, err := cppc.ValidateCreate()
            Expect(err).To(HaveOccurred())
        })
    })
})
```

## Score 5 Criteria
- Calls existing `ValidateArchitecturesSet()` (not reimplementing it)
- Applied in BOTH `ValidateCreate` AND `ValidateUpdate`
- Uses `field.Invalid` for structured error (not a raw `fmt.Errorf`)
- Includes unit test using builder API and Ginkgo structure
- Nil-guards `Spec.Plugins` and `Spec.Plugins.NodeAffinityScoring` before calling
