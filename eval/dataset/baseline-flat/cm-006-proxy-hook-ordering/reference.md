# Reference: Fix Proxy Hook Ordering in generic_deployment_controller.go

## File to Modify

`pkg/controller/certmanager/generic_deployment_controller.go`

## The Bug

In `newGenericDeploymentController`, the `hooks` slice had this ordering:

```go
withContainerEnvOverrideHook(...),  // user override runs first
withProxyEnv,                       // proxy runs second — overwrites user overrides
```

`mergeContainerEnvs` (in `deployment_helper.go`) uses the second argument as the
override: when two env vars share the same name, the second slice wins. So proxy
values were clobbering user-specified container env overrides.

## The Fix

Swap the two entries so `withProxyEnv` runs first:

```go
withProxyEnv,                       // proxy runs first
withContainerEnvOverrideHook(       // user override runs second — wins on conflict
    certManagerOperatorInformers.Operator().V1alpha1().CertManagers(),
    deployment.Name,
    getOverrideEnvFor,
),
```

The surrounding hooks (`withContainerArgsValidateHook` before and
`withContainerEnvValidateHook` after) remain in their current positions.

## No Make Target Required

This is a pure Go source change. No manifests or code generation needed.

## Score-5 Criteria

- Exactly two adjacent lines swapped in the hooks slice
- `withProxyEnv` appears immediately before `withContainerEnvOverrideHook`
- No other hooks reordered or removed
- No other files modified
