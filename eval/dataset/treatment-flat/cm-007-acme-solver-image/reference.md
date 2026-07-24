# Reference: Fix ACME Solver Image in deployment_overrides.go

## File to Modify

`pkg/controller/certmanager/deployment_overrides.go`

## The Bugs

Inside `withOperandImageOverrideHook`, the block that appends `--acme-http01-solver-image`:

```go
// BUGGY VERSION
if len(deployment.Spec.Template.Spec.Containers) == 1 && deployment.Name == certmanagerCAinjectorDeployment {
    deployment.Spec.Template.Spec.Containers[0].Args = common.MergeContainerArgs(
        deployment.Spec.Template.Spec.Containers[0].Args,
        []string{fmt.Sprintf("--acme-http01-solver-image=%s",
            certManagerImage(deployment.Spec.Template.Spec.Containers[0].Image))})
}
```

Two bugs:
1. `certmanagerCAinjectorDeployment` should be `certmanagerControllerDeployment` — the
   `--acme-http01-solver-image` flag only applies to the cert-manager controller, not the
   cainjector.
2. `deployment.Spec.Template.Spec.Containers[0].Image` should be `upstreamACMESolverImage`
   — the acme-http01-solver is a separate image (`quay.io/jetstack/cert-manager-acmesolver`),
   not the controller image.

## The Fix

```go
// CORRECT VERSION
if len(deployment.Spec.Template.Spec.Containers) == 1 && deployment.Name == certmanagerControllerDeployment {
    deployment.Spec.Template.Spec.Containers[0].Args = common.MergeContainerArgs(
        deployment.Spec.Template.Spec.Containers[0].Args,
        []string{fmt.Sprintf("--acme-http01-solver-image=%s",
            certManagerImage(upstreamACMESolverImage))})
}
```

## Relevant Constants

- `certmanagerControllerDeployment = "cert-manager"` (defined in `common.go`)
- `upstreamACMESolverImage = "quay.io/jetstack/cert-manager-acmesolver"` (defined in
  `deployment_overrides.go` ~line 44)

## No Make Target Required

Pure Go source change. No code generation needed.

## Score-5 Criteria

- `certmanagerCAinjectorDeployment` replaced with `certmanagerControllerDeployment`
- `deployment.Spec.Template.Spec.Containers[0].Image` replaced with `certManagerImage(upstreamACMESolverImage)`
- No other logic changed
- No other files modified
