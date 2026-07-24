# Reference: Fix Runtime Endianness Detection in tracepoint.go

## File to Modify

`internal/controller/enoexecevent/daemon/internal/tracepoint/tracepoint.go`

## Change 1: Add order Field to Tracepoint Struct

```go
type Tracepoint struct {
    // ... existing fields ...
    order binary.ByteOrder
}
```

## Change 2: Runtime Detection in NewTracepoint()

Add before the struct literal:

```go
var i uint16 = 0x0001
b := (*[2]byte)(unsafe.Pointer(&i))
// Little endian: b[0] == 0x01
// Big endian:    b[0] == 0x00
var order binary.ByteOrder
if b[0] == 0x00 {
    order = binary.BigEndian
    fmt.Println("Detected big endian architecture")
} else {
    order = binary.LittleEndian
    fmt.Println("Detected little endian architecture")
}
```

Add `order: order,` to the `Tracepoint{...}` struct literal.

## Change 3: Use tp.order in processRecord, Change int32 to uint32

```go
// Before (buggy):
var order binary.ByteOrder = binary.LittleEndian
if binary.LittleEndian.Uint16([]byte{1, 0}) != 1 {
    order = binary.BigEndian
}
realParentTGID := int32(order.Uint32(record.RawSample[:4]))
currentTaskTGID := int32(order.Uint32(record.RawSample[4:8]))

// After (correct):
realParentTGID := tp.order.Uint32(record.RawSample[:4])
currentTaskTGID := tp.order.Uint32(record.RawSample[4:8])
```

The loop variable type changes from `int32` to `uint32`:
```go
for _, pid := range []uint32{currentTaskTGID, realParentTGID} {
```

## Import Required

`"unsafe"` — add to import block.

## Why unsafe.Pointer Works

`var i uint16 = 0x0001` stores the value in memory. On little-endian systems the
low byte (0x01) is at the lower address; on big-endian the high byte (0x00) is at the
lower address. Casting via `unsafe.Pointer` reads the actual bytes without interpretation.

## Score-5 Criteria

- `order binary.ByteOrder` field added to `Tracepoint` struct
- Runtime detection using `(*[2]byte)(unsafe.Pointer(&i))` pattern (not the constant expression)
- `order` stored in struct literal in `NewTracepoint()`
- `processRecord` uses `tp.order` instead of local variable
- TGID values use `uint32` not `int32`
- `"unsafe"` added to imports
