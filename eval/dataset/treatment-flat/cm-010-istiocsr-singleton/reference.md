# Reference: Fix IstioCSR Singleton Enforcement

## File to Modify

`pkg/controller/istiocsr/utils.go`

## The Fix

In `disallowMultipleIstioCSRInstances` (around line 516), change the skip condition from:

```go
if item.GetNamespace() == istiocsr.Namespace {
    continue
}
```

to:

```go
if item.GetNamespace() == istiocsr.Namespace && item.GetName() == istiocsr.Name {
    continue
}
```

## Why This Fixes the Bug

The loop iterates over all IstioCSR instances to find if a conflict exists (an instance
older or equal in age to the current one). The current instance must be skipped to avoid
comparing against itself. The original code skips every instance in the same namespace,
meaning two IstioCSRs in the same namespace (`cert-manager/a` and `cert-manager/b`) are
both skipped during each other's checks — neither detects the other as a conflict. Both
proceed with reconciliation simultaneously.

The fix skips only the exact current instance (matching both namespace AND name). A
same-namespace duplicate is then compared by timestamp and correctly triggers
`ignoreProcessing = true` for the newer instance.

## No Make Target Required

Pure Go source change.

## Score-5 Criteria

- The skip condition uses `&&` to combine namespace and name checks
- `item.GetName() == istiocsr.Name` is the added condition
- No other logic in the function is changed
- The function signature and return values are unchanged
