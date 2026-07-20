# Reference: Add validateDeploymentManifest to IstioCSR

## Pattern Source
Copy and adapt the `validateDeploymentManifest` function from
`pkg/controller/trustmanager/deployments.go`. It should:
1. Check that the expected container name (`istiocsrContainerName` constant) exists
2. Check that required volumes are present
3. Return an error if any check fails — the calling function returns early

## Implementation in `pkg/controller/istiocsr/deployments.go`

```go
const istiocsrContainerName = "istio-csr"

func validateDeploymentManifest(deployment *appsv1.Deployment) error {
    // Verify the expected container exists
    found := false
    for _, c := range deployment.Spec.Template.Spec.Containers {
        if c.Name == istiocsrContainerName {
            found = true
            break
        }
    }
    if !found {
        return fmt.Errorf("deployment manifest missing expected container %q", istiocsrContainerName)
    }
    return nil
}
```

Call it at the start of the mutation pipeline function, before any mutation functions run:
```go
func mutateDeployment(deployment *appsv1.Deployment, ...) error {
    if err := validateDeploymentManifest(deployment); err != nil {
        return fmt.Errorf("invalid IstioCSR deployment manifest from bindata: %w", err)
    }
    // ... mutation functions ...
}
```

## Unit Test

```go
func TestValidateDeploymentManifest(t *testing.T) {
    tests := []struct {
        name       string
        deployment *appsv1.Deployment
        wantErr    bool
    }{
        {
            name: "valid manifest with correct container",
            deployment: &appsv1.Deployment{
                Spec: appsv1.DeploymentSpec{
                    Template: corev1.PodTemplateSpec{
                        Spec: corev1.PodSpec{
                            Containers: []corev1.Container{
                                {Name: istiocsrContainerName},
                            },
                        },
                    },
                },
            },
            wantErr: false,
        },
        {
            name:       "empty containers list",
            deployment: &appsv1.Deployment{},
            wantErr:    true,
        },
        {
            name: "wrong container name",
            deployment: &appsv1.Deployment{
                Spec: appsv1.DeploymentSpec{
                    Template: corev1.PodTemplateSpec{
                        Spec: corev1.PodSpec{
                            Containers: []corev1.Container{
                                {Name: "wrong-name"},
                            },
                        },
                    },
                },
            },
            wantErr: true,
        },
    }
    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            err := validateDeploymentManifest(tt.deployment)
            if (err != nil) != tt.wantErr {
                t.Errorf("validateDeploymentManifest() error = %v, wantErr %v", err, tt.wantErr)
            }
        })
    }
}
```

## Score 5 Criteria
- Validation function mirrors TrustManager's pattern (not a novel approach)
- Called BEFORE any mutation functions run (guard at pipeline entry)
- Returns early with a descriptive error wrapping the specific violation
- Table-driven test with at least 3 cases: valid, missing container, wrong container name
- Container name uses a named constant (not a raw string literal in the check)
