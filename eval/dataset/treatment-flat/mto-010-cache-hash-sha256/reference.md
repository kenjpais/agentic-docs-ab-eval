# Reference: Fix Cache Hash to Use SHA-256 (MULTIARCH-5646)

## File to Modify

`pkg/image/cache.go`

## The Rewrite

Replace the `computeHash` function:

```go
func computeHash(imageReference string, secrets []byte) string {
    h := sha256.New()
    h.Write([]byte(imageReference))
    h.Write([]byte{0})
    h.Write(secrets)
    return hex.EncodeToString(h.Sum(nil))
}
```

## Import Change

Remove `"hash/fnv"` and add `"crypto/sha256"`.

The full import block becomes:
```go
import (
    "context"
    "crypto/sha256"
    "encoding/hex"
    "time"
    ...
)
```

## Key Logic

- `sha256.New()` produces a 256-bit digest — collision-resistant unlike FNV-128's 128-bit
  non-cryptographic output.
- `h.Write([]byte{0})` — the null byte separator between imageReference and secrets prevents
  length-extension boundary confusion: `hash("a" + "bc")` != `hash("ab" + "c")`.
- The rest of the function is unchanged: `hex.EncodeToString(h.Sum(nil))` produces the
  same hex-string format, so the cache key type is compatible.

## No Make Target Required

Pure Go source change.

## Score-5 Criteria

- `sha256.New()` used (not fnv.New128() or any other hash)
- `h.Write([]byte{0})` null byte separator written between imageReference and secrets
- `"hash/fnv"` import removed; `"crypto/sha256"` import added
- `hex.EncodeToString(h.Sum(nil))` return value preserved
- No other function in cache.go is changed
