# Reference: Add Image Cache Hit Metric

## Metric Name and Type
Counter: `mto_ppo_ctrl_image_cache_hits_total`
Label: `image_ref` (string, the full image reference that was cache-hit)
Type: `prometheus.CounterVec` (not Gauge, not Histogram)

The `mto_ppo_ctrl_` prefix is the correct prefix for controller-side metrics.
Webhook metrics use `mto_ppo_wh_*`. Using the wrong prefix is a convention violation.

## Registration in `internal/controller/podplacement/metrics/`

Follow the existing pattern for CounterVec registration:
```go
var ImageCacheHitsTotal = prometheus.NewCounterVec(
    prometheus.CounterOpts{
        Name: "mto_ppo_ctrl_image_cache_hits_total",
        Help: "Total number of image architecture lookups served from cache.",
    },
    []string{"image_ref"},
)

func init() {
    metrics.Registry.MustRegister(ImageCacheHitsTotal)
}
```

## Instrumentation in `pkg/image/cache.go` or `pkg/image/facade.go`

In the function that returns cached architecture results (before returning the cached value,
not in the registry-fetch path):
```go
podplacementmetrics.ImageCacheHitsTotal.WithLabelValues(imageRef).Inc()
```

## Key Conventions
- Controller metrics prefix: `mto_ppo_ctrl_*` (NOT `mto_image_*` or `image_cache_*`)
- Use `CounterVec` for this metric type (counts, never decrements) — not Gauge
- `image_ref` label captures per-image granularity for SLI monitoring
- Registration via `metrics.Registry.MustRegister` in the metrics package init()

## Score 5 Criteria
- Correct metric name with `mto_ppo_ctrl_` prefix
- CounterVec (not Counter or Gauge) with `image_ref` label
- Registration follows existing package pattern
- Instrumented in cache return path (not the registry fetch path)
