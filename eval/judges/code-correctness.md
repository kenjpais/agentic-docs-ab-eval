You are evaluating the technical correctness of a Go implementation for a Kubernetes operator task.

## Reference Implementation (Task + Expected Approach)
{{ outputs.annotation_reference_content }}

## Agent's Implementation
{{ conversation }}

## What to Check

Evaluate the agent's implementation for:

1. **Go type correctness**: Are the types correct? (e.g., `*int32` vs `int32`, pointer receivers, correct struct embedding)
2. **Kubebuilder markers**: Are markers syntactically valid? (e.g., `+kubebuilder:validation:Minimum=1` not `+kubebuilder:validation:min=1`)
3. **CEL rule syntax**: If CEL rules are written, is the syntax correct? (e.g., `self.metadata.name == 'cluster'`, not Python-style `==`)
4. **Existing API usage**: Does the code call methods and access fields that actually exist in the referenced packages?
5. **Import paths**: Are Go import paths correct for this repository's module structure?
6. **No invented APIs**: Does the code avoid calling functions or methods that don't exist in the codebase?
7. **Make target names**: Are referenced `make` targets real targets that exist in this repository's Makefile?
8. **Conversion function signatures**: If conversion functions are added, do they match the expected signatures used by controller-gen?

## Scoring Rubric

**5 — Fully correct**: All types, APIs, markers, CEL rules, and imports are correct. No invented methods. The code would compile and function correctly.

**4 — Mostly correct**: 1–2 minor issues (e.g., slightly wrong marker syntax, one incorrect import path, one method name off by one character). Easily fixable.

**3 — Partially correct**: Some correct code but notable errors (e.g., calling a method that doesn't exist, wrong kubebuilder marker format throughout, or CEL syntax that would fail validation). Requires real fixes.

**2 — Many errors**: Multiple type errors, wrong APIs, or invented packages/methods throughout. Would not compile.

**1 — Fundamentally broken**: Shows basic misunderstanding of Go or Kubernetes operator API conventions. Most of the implementation is wrong.

Respond in this format:
Score: <integer 1-5>
Justification: <2-3 sentences identifying any errors found, or confirming correctness>
