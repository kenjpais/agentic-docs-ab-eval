# Reference: Console Resources Conditional Controller (OCPBUGS-85579)

## Files to Modify / Create

- `pkg/operator/starter.go` — add console API discovery
- `pkg/controller/certmanager/console_resources.go` — new file
- `pkg/controller/certmanager/cert_manager_controller_set.go` — register new controller

## Change 1: starter.go — Console API Discovery

After the Infrastructure `InitInformerIfAvailable` block, add:

```go
import consolev1 "github.com/openshift/api/console/v1"

// inside RunOperator, after optInfraInformer block:
consolev1GVR := consolev1.GroupVersion.WithResource("consoleyamlsamples")
consoleDiscovered, err := utils.NewResourceDiscoverer(consolev1GVR, configClient.Discovery()).Discover()
if err != nil {
    return fmt.Errorf("failed to discover Console API presence: %w", err)
}
```

Then pass `consoleDiscovered` to `certmanager.NewCertManagerControllerSet(...)`.

## Change 2: console_resources.go — New Controller

```go
package certmanager

import (
    "github.com/openshift/library-go/pkg/controller/factory"
    "github.com/openshift/library-go/pkg/operator/events"
    "github.com/openshift/library-go/pkg/operator/resource/resourceapply"
    "github.com/openshift/library-go/pkg/operator/staticresourcecontroller"
    "github.com/openshift/library-go/pkg/operator/v1helpers"

    "github.com/openshift/cert-manager-operator/pkg/operator/assets"
)

const certManagerConsoleResourcesControllerName = operatorName + "-console-resources"

var certManagerConsoleAssetFiles = []string{
    "consoles/cert-manager-acme-issuer-sample.yaml",
    "consoles/cert-manager-certificate-sample.yaml",
    "consoles/cert-manager-example-quickstart.yaml",
    "consoles/cert-manager-issuer-sample.yaml",
}

func NewCertManagerConsoleResourcesController(
    operatorClient v1helpers.OperatorClient,
    kubeClientContainer *resourceapply.ClientHolder,
    consoleApplicable bool,
    eventsRecorder events.Recorder,
) factory.Controller {
    return staticresourcecontroller.NewStaticResourceController(
        certManagerConsoleResourcesControllerName,
        assets.Asset,
        []string{},
        kubeClientContainer,
        operatorClient,
        eventsRecorder,
    ).WithConditionalResources(
        assets.Asset,
        certManagerConsoleAssetFiles,
        func() bool { return consoleApplicable },
        nil,
    )
}
```

## Change 3: cert_manager_controller_set.go — Register Controller

Add field to `CertManagerControllerSet`:
```go
certManagerConsoleResourcesController factory.Controller
```

Add parameter to `NewCertManagerControllerSet`:
```go
consoleApplicable bool,
```

Initialize in the struct literal:
```go
certManagerConsoleResourcesController: NewCertManagerConsoleResourcesController(
    operatorClient,
    kubeClientContainer,
    consoleApplicable,
    eventRecorder,
),
```

Include in `ToArray()`:
```go
c.certManagerConsoleResourcesController,
```

## Why This Fixes the Bug

`WithConditionalResources` with `func() bool { return consoleApplicable }` ensures the
console assets are never applied when the Console API is absent. The `consoleApplicable`
flag is set once at startup via API discovery and remains stable for the operator's lifetime.

## No Make Target Required (for code changes)

The bindata must be regenerated separately (`make bindata` after placing console YAML files
in `bindata/consoles/`), but the controller code itself needs no build step.

## Score-5 Criteria

- `consolev1GVR := consolev1.GroupVersion.WithResource("consoleyamlsamples")` used in starter.go
- `utils.NewResourceDiscoverer(...).Discover()` called; error checked and wrapped
- `certManagerConsoleResourcesControllerName = operatorName + "-console-resources"` constant defined
- `certManagerConsoleAssetFiles` lists exactly 4 console asset paths under `"consoles/"`
- `staticresourcecontroller.NewStaticResourceController` called with `[]string{}` initial files
- `.WithConditionalResources(assets.Asset, certManagerConsoleAssetFiles, func() bool { return consoleApplicable }, nil)` chained
- `CertManagerControllerSet` struct updated with new controller field
- `NewCertManagerControllerSet` accepts `consoleApplicable bool`
- Controller included in `ToArray()` return slice
