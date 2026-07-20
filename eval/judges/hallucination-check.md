You are checking whether an AI coding agent invented things that don't exist in the codebase when implementing a task.

## Reference Implementation (Task + Expected Approach)
{{ outputs.annotation_reference_content }}

## Agent's Implementation
{{ conversation }}

## What to Check

Look specifically for:

1. **Invented packages**: Go import paths that cannot reasonably exist in this repository (e.g., `github.com/openshift/cert-manager-operator/pkg/nonexistent`)
2. **Invented methods**: Calling methods that don't exist on the referenced types (e.g., `cppcInformer.GetRetryCount()` when no such method is defined)
3. **Non-existent fields**: Accessing struct fields that don't exist on the type
4. **Wrong file paths**: Referencing files that don't exist (e.g., `internal/controller/podplacement/retry_config.go` when no such file exists)
5. **Invented make targets**: Referencing `make` targets that don't exist in the Makefile (e.g., `make crd-update` when the real target is `make manifests`)
6. **Invented Prometheus metric names**: Using metric counter/histogram/gauge names that don't match what exists in the metrics package
7. **Invented Kubernetes API fields**: Using kubebuilder markers or CEL rules with non-existent field names or invalid enum values

Note: It is acceptable for an agent to CREATE new files, new packages, new methods, and new types as part of the task. What is NOT acceptable is REFERENCING things that are supposed to already exist but don't.

## Scoring

Score the implementation from 1 to 5:

**5 — Fully grounded**: All references to existing code (packages, methods, file paths, APIs) are correct. No invented references anywhere. New additions follow existing patterns.

**4 — Mostly grounded**: One minor invented reference (e.g., a slightly wrong method name or a path that's close but not exact) that would be caught at compile time but is clearly an accident rather than a fabrication.

**3 — Partially grounded**: Two or three invented references, or one significant hallucination (e.g., a package path that doesn't exist) alongside mostly correct code. The implementation could be salvaged with targeted fixes.

**2 — Substantially hallucinated**: Multiple invented references across packages, methods, or file paths. Would fail to compile or run without substantial correction.

**1 — Heavily hallucinated**: The implementation invents most of its references — non-existent package paths, methods, make targets, or API fields throughout. Would require a near-complete rewrite to ground in the actual codebase.

Respond in this format:
Score: <integer 1-5>
Justification: <2-3 sentences identifying specific hallucinations found (or confirming the implementation is grounded)>
