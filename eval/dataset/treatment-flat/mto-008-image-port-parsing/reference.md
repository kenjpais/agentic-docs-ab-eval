# Reference: Fix parseImageReference for Registries with Ports

## File to Modify

`pkg/image/inspector.go`

## The Rewrite

Replace the `strings.Split`-based implementation with:

```go
func parseImageReference(imageName string) (string, error) {
    if imageName == "" {
        return "", errors.New("invalid image name, must not be empty")
    }
    digestIdx := strings.Index(imageName, "@sha")
    switch digestIdx {
    case -1:
        return imageName, nil
    case 0:
        return "", errors.New("invalid image name, image must not be empty")
    default:
    }
    if strings.Count(imageName[digestIdx+1:], "@sha") > 0 {
        return "", errors.New("invalid image name, must only have one digest")
    }
    namePart := imageName[:digestIdx]
    digestPart := imageName[digestIdx:]
    lastSlash := strings.LastIndex(namePart, "/")
    lastColon := strings.LastIndex(namePart, ":")
    switch {
    case lastColon == -1:
        return imageName, nil
    case lastColon > lastSlash:
        namePart = namePart[:lastColon]
        return namePart + digestPart, nil
    default:
        return imageName, nil
    }
}
```

## Key Logic

- `digestIdx = strings.Index(imageName, "@sha")` finds the digest separator without
  hardcoding `@sha256:`, so `@sha384:` and `@sha512:` work too.
- `lastColon > lastSlash`: if the last colon comes after the last slash, it separates
  a tag — strip it. Otherwise the colon is part of `host:port` — keep it.

## Examples

| Input | Output |
|-------|--------|
| `registry.io:5000/nginx:latest@sha256:abc` | `registry.io:5000/nginx@sha256:abc` |
| `registry.io/nginx:latest@sha256:abc` | `registry.io/nginx@sha256:abc` |
| `registry.io/nginx@sha256:abc` | `registry.io/nginx@sha256:abc` (unchanged) |
| `registry.io:5000/nginx@sha256:abc` | `registry.io:5000/nginx@sha256:abc` (unchanged) |
| `""` | error: "invalid image name, must not be empty" |

## No Make Target Required

Pure Go source change.

## Score-5 Criteria

- `strings.Index(imageName, "@sha")` used for digest detection (not `strings.Split` on `@sha256:`)
- `strings.LastIndex` used for both `/` and `:`
- `lastColon > lastSlash` condition correctly distinguishes tag from port
- Duplicate-digest check: `strings.Count(imageName[digestIdx+1:], "@sha") > 0`
- Empty string handled at top of function
