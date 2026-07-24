# Reference: Expand Bundle Image Detection to 7 Annotations

## File to Modify

`pkg/image/inspector.go`

## Step 1: Define 7 Constants

Replace the single `operatorSDKBuilderBundleAnnotation` constant with all 7:

```go
const (
    osdkMetricsAnnotation              = "operators.operatorframework.io.metrics.builder"
    osdkMediaTypeAnnotation            = "operators.operatorframework.io.bundle.mediatype.v1"
    osdkManifestsAnnotation            = "operators.operatorframework.io.bundle.manifests.v1"
    osdkBundleMetadataAnnotation       = "operators.operatorframework.io.bundle.metadata.v1"
    osdkBundlePackageAnnotation        = "operators.operatorframework.io.bundle.package.v1"
    osdkBundleChannelsAnnotation       = "operators.operatorframework.io.bundle.channels.v1"
    osdkBundleDefaultChannelAnnotation = "operators.operatorframework.io.bundle.channel.default.v1"
)
```

## Step 2: Define a Set in a var Block

```go
var (
    // https://github.com/operator-framework/operator-registry/blob/c4b5f1196/docs/design/operator-bundle.md
    operatorSDKBuilderBundleAnnotationSet = sets.New[string](
        osdkMetricsAnnotation, osdkMediaTypeAnnotation, osdkManifestsAnnotation,
        osdkBundleMetadataAnnotation, osdkBundlePackageAnnotation,
        osdkBundleChannelsAnnotation, osdkBundleDefaultChannelAnnotation)
)
```

## Step 3: Extract isBundleImage Helper

```go
func isBundleImage(image ociv1.ImageConfig) bool {
    for label := range image.Labels {
        if operatorSDKBuilderBundleAnnotationSet.Has(label) {
            return true
        }
    }
    return false
}
```

## Step 4: Replace Inline Check in GetCompatibleArchitecturesSet

Old inline check:
```go
if _, ok := config.Config.Labels[operatorSDKBuilderBundleAnnotation]; ok {
```

New call:
```go
if isBundleImage(config.Config) {
```

## Import Required

`ociv1 "github.com/opencontainers/image-spec/specs-go/v1"` — check if already present,
add to imports if not.

## No Make Target Required

Pure Go source change. Run `go build ./...` to verify compilation.

## Score-5 Criteria

- All 7 constants defined with correct annotation strings
- `sets.New[string]` var block containing all 7 constants
- `isBundleImage(image ociv1.ImageConfig) bool` helper using `operatorSDKBuilderBundleAnnotationSet.Has()`
- Call site in `GetCompatibleArchitecturesSet` updated to use `isBundleImage(config.Config)`
