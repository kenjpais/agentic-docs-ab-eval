You are evaluating whether an AI coding agent successfully completed a Kubernetes operator implementation task.

## Reference Implementation (Task + Expected Approach)
{{ outputs.annotation_reference_content }}

## Agent's Implementation
{{ conversation }}

## Scoring Rubric

Score the agent's implementation from 1 to 5:

**5 — Fully correct**: All required files are identified and modified correctly. All sub-tasks are addressed (API changes, code generation commands, conversion functions, wiring, etc.). The implementation would work as-is and would pass code review.

**4 — Mostly correct**: The main implementation is correct with minor gaps (e.g., missing one make command, missing a secondary file update, or forgetting to update one related function). A reviewer would accept it with minor comments.

**3 — Partially correct**: The core approach is right but significant gaps remain (e.g., correct API field added but CPPC informer wiring missing, or wrong make command ordering stated). Requires non-trivial fixes before it would work.

**2 — Minimal attempt**: Some relevant code is produced but the implementation is substantially incomplete or takes the wrong approach. Core elements are missing or incorrect.

**1 — Not attempted or fundamentally wrong**: The agent failed to produce a meaningful implementation, refused the task, produced something completely off-topic, or proposed an approach that is fundamentally contrary to how this codebase works.

## Instructions

1. Compare the agent's implementation against the reference.
2. Identify which sub-tasks were completed correctly and which were missed or wrong.
3. Assign a score from 1 to 5.
4. Provide a brief justification (2–3 sentences) naming what was done right and what was missing or wrong.

Respond in this format:
Score: <integer 1-5>
Justification: <2-3 sentences>
