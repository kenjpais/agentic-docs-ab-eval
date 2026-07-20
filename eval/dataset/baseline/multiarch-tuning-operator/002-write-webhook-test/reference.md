# Reference: Ginkgo Test for System Namespace Exclusion

## Correct Approach

The test must live inside the existing `Describe("MutatingWebhook")` block and follow
the existing `Context/It` pattern. It must use the `pkg/testing/builder` fluent API.

```go
Context("when a pod is created in a system namespace", func() {
    It("should NOT assign the scheduling gate to pods in openshift-kube-apiserver", func() {
        pod := builder.NewPod().
            WithName("test-pod").
            WithNamespace("openshift-kube-apiserver").
            Build()

        // Create the pod via the test client (which triggers the webhook)
        Expect(k8sClient.Create(ctx, pod)).To(Succeed())

        // Verify the scheduling gate was NOT added
        createdPod := &corev1.Pod{}
        Expect(k8sClient.Get(ctx, client.ObjectKeyFromObject(pod), createdPod)).To(Succeed())
        Expect(createdPod.Spec.SchedulingGates).To(BeEmpty())
    })
})
```

## Key Conventions

- Uses `builder.NewPod().WithName(...).WithNamespace(...).Build()` — NOT `&corev1.Pod{...}` struct literal
- Uses Ginkgo's `Context/It` DSL — NOT `t.Run(...)` or raw `func Test*`
- The test framework is envtest-based; use `k8sClient` (already set up by suite)
- Assertion uses `BeEmpty()` to verify no scheduling gate — not a len check
- System namespace exclusion is unconditional: `openshift-*`, `kube-*`, `hypershift-*` are always excluded

## Why the Namespace Exclusion Matters (Security Context)
This is a security control, not a convenience feature. System namespaces are excluded
unconditionally to prevent the operator from interfering with cluster control plane pods.
The test should verify the exclusion holds even with a permissive namespaceSelector.

## Score 5 Criteria
- Uses fluent builder API (not struct literal)
- Uses Ginkgo Describe/Context/It structure
- Asserts scheduling gate is absent (not just checks a field)
- Correctly uses `openshift-kube-apiserver` as the system namespace
- Follows existing test file structure and import patterns
