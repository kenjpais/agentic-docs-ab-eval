# Reference: Add Fifth Execution Mode

## New File: `internal/controller/metricsaggregator/reconciler.go`

```go
package metricsaggregator

import (
    "context"
    ctrl "sigs.k8s.io/controller-runtime"
    "sigs.k8s.io/controller-runtime/pkg/manager"
)

type MetricsAggregatorReconciler struct{}

func (r *MetricsAggregatorReconciler) Reconcile(ctx context.Context, req ctrl.Request) (ctrl.Result, error) {
    return ctrl.Result{}, nil
}

func (r *MetricsAggregatorReconciler) SetupWithManager(mgr manager.Manager) error {
    return ctrl.NewControllerManagedBy(mgr).
        Named("metrics-aggregator").
        Complete(r)
}
```

## Changes to `cmd/main.go`

### 1. Add the flag
In `bindFlags`:
```go
fs.BoolVar(&enableMetricsAggregator, "enable-metrics-aggregator", false,
    "Enable the metrics aggregator controller.")
```

Also add mutual exclusion in the flags validation section:
```go
if moreThanOneTrue(enableOperator, enablePPCControllers, enablePPCWebhook, enableEnoexecEventControllers, enableMetricsAggregator) {
    // error: only one mode can be enabled
}
```

### 2. Add leader election ID
```go
const metricsAggregatorLeaderElectionID = "multiarch-tuning-operator-metrics-aggregator.multiarch.openshift.io"
```

Each mode has its own leader election ID — this allows independent HA deployments.
Using the same ID as another mode would cause leader election conflicts.

### 3. Add the mode dispatch block
```go
if enableMetricsAggregator {
    mgr, err := ctrl.NewManager(cfg, ctrl.Options{
        LeaderElection:   true,
        LeaderElectionID: metricsAggregatorLeaderElectionID,
        // ... shared options
    })
    // Start CPPC informer
    // Setup MetricsAggregatorReconciler
    reconciler := &metricsaggregator.MetricsAggregatorReconciler{}
    if err := reconciler.SetupWithManager(mgr); err != nil {
        setupLog.Error(err, "unable to setup MetricsAggregatorReconciler")
        os.Exit(1)
    }
    if err := mgr.Start(ctx); err != nil {
        setupLog.Error(err, "unable to run metrics aggregator manager")
        os.Exit(1)
    }
}
```

## Key Conventions
- Each mode has its own unique `LeaderElectionID` constant — never share with another mode
- Modes are mutually exclusive — `moreThanOneTrue()` or equivalent check enforces this
- CPPC informer must be started before the manager if the controller needs CPPC config
- Leader election ID format: `<operator-name>-<mode>.<domain>`

## Score 5 Criteria
- Unique leader election ID constant with correct naming format
- Mutual exclusion updated to include the new flag
- CPPC informer started in the new mode's setup block
- `SetupWithManager` follows the same pattern as existing modes
- New package created at `internal/controller/metricsaggregator/`
