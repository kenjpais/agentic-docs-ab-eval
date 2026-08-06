# Reference: Fix Docker Certificates Volume Path (MULTIARCH-5646)

## File to Modify

`internal/controller/operator/podplacement_objects.go`

## Change 1: Volume Definition

In the `buildControllerDeployment` function's additional volumes slice, change the
`"docker-conf"` volume:

```go
{
    Name: "docker-conf",
    VolumeSource: corev1.VolumeSource{
        HostPath: &corev1.HostPathVolumeSource{
            Path: "/etc/docker/certs.d/",
            Type: utils.NewPtr(corev1.HostPathDirectoryOrCreate),
        },
    },
},
```

(Was `"/etc/docker/"` with `corev1.HostPathDirectory`.)

## Change 2: VolumeMount

In the `additionalMounts` slice, update the `"docker-conf"` mount path:

```go
{
    Name:      "docker-conf",
    MountPath: "/etc/docker/certs.d/",
    ReadOnly:  true,
},
```

(Was `"/etc/docker/"`)

## Why Both Changes Are Needed

- **Path**: Docker reads per-registry TLS certificates from `/etc/docker/certs.d/<hostname>/`,
  not from `/etc/docker/`. The image inspector calls `DockerCertsDir()` and sets
  `sys.DockerPerHostCertDirPath` to the value of `DOCKER_CERTS_DIR` env var. The env var is
  expected to point at the directory that contains per-host cert subdirectories — i.e. the
  mount point, which must be `/etc/docker/certs.d/`.
- **Type**: `HostPathDirectory` fails if the directory does not already exist on the node.
  Fresh nodes without custom Docker cert configuration do not have `/etc/docker/certs.d/`,
  so the pod fails to start. `HostPathDirectoryOrCreate` silently creates the directory when
  absent.

## No Make Target Required

Pure Go source change.

## Score-5 Criteria

- Volume `Path` changed to `"/etc/docker/certs.d/"` (trailing slash preserved)
- Volume `Type` changed to `corev1.HostPathDirectoryOrCreate`
- VolumeMount `MountPath` changed to `"/etc/docker/certs.d/"`
- `ReadOnly: true` preserved on the VolumeMount
- No other volumes or mounts are changed
